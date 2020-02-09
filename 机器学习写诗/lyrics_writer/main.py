# coding=utf-8
from __future__ import print_function
import os
import sys
import time
import random
import numpy as np
import tensorflow as tf

from tensorflow.contrib import legacy_seq2seq as seq2seq


'''
使用的了sequence-to-sequence模型以及RNN网络进行歌词语义的学习以及建模
'''

# 用flags模块传入参数，这里我用它传入数据集名称，并且为了方便，checkpoint存储目录与数据集共享名字
tf.app.flags.DEFINE_string('cd', '', """and checkpoint.""")  # 'cd' 即 checkpointDir，存放checkpoint的目录
FLAGS = tf.app.flags.FLAGS


class Param():
    '''训练参数设置 '''
    batch_size = 128         # 每批数据量的大小  batch_size越小，一个batch的随机性越大，越不易收敛，
    n_epoch = 10            # 全部样本训练几遍
    learning_rate = 0.01    # 学习率
    decay_steps = 1000      # 每多少batch衰减一次。 采用学习率不断衰减，梯度下降来平衡训练速度和loss损失，得到最佳学习效果
    decay_rate = 0.9        # 衰减率
    grad_clip = 5           # 简单粗暴的使用梯度剪切防止梯度消失/爆炸

    state_size = 100        # state大小
    num_layers = 3          # 模型层数
    seq_length = 20         # 序列长度
    log_dir = './logs'      # 存储日志
    # gen_num = 200           # 生成的诗歌的长度


class DataGet():

    def __init__(self, datafiles, args):
        self.seq_length = args.seq_length
        self.batch_size = args.batch_size
        with open(datafiles, encoding='utf-8') as f:
            self.data = f.read()
        self.total_len = len(self.data)  # 总数据集的大小
        self.words = list(set(self.data))
        self.words.sort()
        # vocab是vocabulary缩写
        self.vocab_size = len(self.words)  # vocabulary 大小
        print('Vocabulary Size: ', self.vocab_size)
        self.char2id_dict = {w: i for i, w in enumerate(self.words)}
        self.id2char_dict = {i: w for i, w in enumerate(self.words)}

        # 用于生成当前批的指针位置
        self._pointer = 0

    def char2id(self, c):
        return self.char2id_dict[c]

    def id2char(self, id):
        return self.id2char_dict[id]


    def next_batch(self):
        x_batches = []
        y_batches = []
        for i in range(self.batch_size):
            if self._pointer + self.seq_length + 1 >= self.total_len:
                self._pointer = 0
            bx = self.data[self._pointer: self._pointer + self.seq_length]
            by = self.data[self._pointer +
                           1: self._pointer + self.seq_length + 1]
            self._pointer += self.seq_length  # 更新指针的位置

            # 转化为id字段
            bx = [self.char2id(c) for c in bx]
            by = [self.char2id(c) for c in by]
            x_batches.append(bx)
            y_batches.append(by)

        return x_batches, y_batches


class Model():
    '''核心神经网络模型'''
    def __init__(self, args, data, infer=False):
        if infer:
            args.batch_size = 1
            args.seq_length = 1
        with tf.name_scope('inputs'):
            self.input_data = tf.placeholder(
                tf.int32, [args.batch_size, args.seq_length])
            self.target_data = tf.placeholder(
                tf.int32, [args.batch_size, args.seq_length])

        with tf.name_scope('model'):
            self.cell = []
            for n in range(args.num_layers):
                self.cell.append(tf.nn.rnn_cell.LSTMCell(args.state_size))
            self.cell = tf.nn.rnn_cell.MultiRNNCell(self.cell)
            self.initial_state = self.cell.zero_state(
                args.batch_size, tf.float32)
            with tf.variable_scope('rnnlm'):
                w = tf.get_variable(
                    'softmax_w', [args.state_size, data.vocab_size])
                b = tf.get_variable('softmax_b', [data.vocab_size])
                with tf.device("/cpu:0"):
                    embedding = tf.get_variable(
                        'embedding', [data.vocab_size, args.state_size])
                    inputs = tf.nn.embedding_lookup(embedding, self.input_data)
            outputs, last_state = tf.nn.dynamic_rnn(
                self.cell, inputs, initial_state=self.initial_state)

        with tf.name_scope('loss'):
            output = tf.reshape(outputs, [-1, args.state_size])

            self.logits = tf.matmul(output, w) + b
            self.probs = tf.nn.softmax(self.logits)
            self.last_state = last_state

            targets = tf.reshape(self.target_data, [-1])
            loss = seq2seq.sequence_loss_by_example([self.logits],
                                                    [targets],
                                                    [tf.ones_like(targets, dtype=tf.float32)])
            self.cost = tf.reduce_sum(loss) / args.batch_size
            tf.summary.scalar('loss', self.cost)

        with tf.name_scope('optimize'):
            self.lr = tf.placeholder(tf.float32, [])
            tf.summary.scalar('learning_rate', self.lr)

            optimizer = tf.train.AdamOptimizer(self.lr)
            tvars = tf.trainable_variables()
            grads = tf.gradients(self.cost, tvars)
            for g in grads:
                tf.summary.histogram(g.name, g)
            grads, _ = tf.clip_by_global_norm(grads, args.grad_clip)

            self.train_op = optimizer.apply_gradients(zip(grads, tvars))
            self.merged_op = tf.summary.merge_all()


def train(data, model, args):
    '''训练'''
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        checkpoint = tf.train.latest_checkpoint('./'+FLAGS.cd)
        start_iter = 0
        if checkpoint:
            saver.restore(sess, checkpoint)
            print("## restoring checkpoint from: {0}".format(checkpoint))
            start_iter += int(checkpoint.split('-')[-1])
        writer = tf.summary.FileWriter(args.log_dir, sess.graph)
        max_iter = args.n_epoch * \
            (data.total_len // args.seq_length) // args.batch_size

        for i in range(start_iter, max_iter):
            learning_rate = args.learning_rate * \
                (args.decay_rate ** (i // args.decay_steps))
            x_batch, y_batch = data.next_batch()
            feed_dict = {model.input_data: x_batch,
                         model.target_data: y_batch,
                         model.lr: learning_rate}
            train_loss, summary, _, _ = sess.run([model.cost, model.merged_op,
                                                  model.last_state,
                                                  model.train_op], feed_dict)

            if i % 10 == 0:
                writer.add_summary(summary, global_step=i)
                print('Step:{}/{}, training_loss:{:4f}'.format(i, max_iter, train_loss))
            if i % 4000 == 0 or (i + 1) == max_iter: # 4000个样本保存一次
                saver.save(sess, os.path.join('./'+FLAGS.cd, 'model.ckpt'), global_step=i)


# def compose(data, model, args):          # 诗意书写版本
#     saver = tf.train.Saver()
#     with tf.Session() as sess:
#         ckpt = tf.train.latest_checkpoint(args.log_dir)
#         print(ckpt)
#         saver.restore(sess, ckpt)

#         # initial phrase to warm RNN
#         prime = input('输入开头(字词句)： ')
#         state = sess.run(model.cell.zero_state(1, tf.float32))

#         for word in prime[:-1]:
#             x = np.zeros((1, 1))
#             x[0, 0] = data.char2id(word)
#             feed = {model.input_data: x, model.initial_state: state}
#             state = sess.run(model.last_state, feed)

#         word = prime[-1]
#         lyrics = prime
#         for i in range(args.gen_num):
#             x = np.zeros([1, 1])
#             x[0, 0] = data.char2id(word)
#             feed_dict = {model.input_data: x, model.initial_state: state}
#             probs, state = sess.run([model.probs, model.last_state], feed_dict)
#             p = probs[0]
#             word = data.id2char(np.argmax(p))
#             print(word, end='')
#             sys.stdout.flush()
#             time.sleep(0.05)
#             lyrics += word
#         return lyrics


def compose(data, model, args):              # 一口气高效作诗版本
    '''生成诗歌'''
    saver = tf.train.Saver()
    with tf.Session() as sess:
        ckpt = tf.train.latest_checkpoint(os.path.join('./'+FLAGS.cd))
        print(ckpt)
        saver.restore(sess, ckpt)

        # 用户自定义设置诗歌开头
        prime = input('输入开头(字词句)： ')
        state = sess.run(model.cell.zero_state(1, tf.float32))

        for word in prime[:-1]:
            x = np.zeros((1, 1))
            x[0, 0] = data.char2id(word)
            # print(word, x[0, 0])
            feed = {model.input_data: x, model.initial_state: state}
            state = sess.run(model.last_state, feed)

        word = prime[-1]
        lyrics = prime
        for i in range(random.randint(40,320)):  # 诗歌长度随意
            x = np.zeros([1, 1])
            x[0, 0] = data.char2id(word)
            feed_dict = {model.input_data: x, model.initial_state: state}
            probs, state = sess.run([model.probs, model.last_state], feed_dict)
            probs = probs[0]
            index = -(int(abs(np.random.randn())*3)+1)  # 引入随机，防止一直重复生成同一句概率最大的诗歌
            word = data.id2char(np.argsort(probs)[index])
            lyrics += word

            # print(word, end='')
            # sys.stdout.flush()
            # time.sleep(0.05)

        return lyrics


def main(infer):

    args = Param()
    data = DataGet(FLAGS.cd+'.txt', args)
    model = Model(args, data, infer)
    if infer:
        poem = compose(data, model, args)
        print()
        print('-'*40)
        print()
        for i in poem.split('\n'):
            print(' '*6 + i +'\n')
        print()
        print('-'*40)
        print()
    else:
        train(data, model, args)


if __name__ == '__main__':
    os.environ['CUDA_VISIBLE_DEVICES'] = "0"
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    hlp = """
    train:
        python main.py 0 -cd checkpointDir
    compose:
        python main.py 1 -cd checkpointDir
    """

    if len(sys.argv) == 4:     # 判断用户传入参数是否正确
        infer = int(sys.argv[1])
        print('--Composing--' if infer else '--Training--')
        if not os.path.exists('./'+FLAGS.cd):  # 专辑目录
            os.mkdir('./'+FLAGS.cd)
        main(infer)
    else:
        print(hlp)
        sys.exit(1)

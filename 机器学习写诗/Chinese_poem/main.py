# -*- coding: utf-8 -*-

import os
import sys
import tensorflow as tf
import numpy as np
import argparse
import random
import time
import collections

# 不断测试发现250次训练就基本上拟合好了
batchSize = 64            # 每次batch大小
epochNum = 250            # 继续训练多少个epoch
generateNum = 5           # 每次生成诗歌数量
saveStep = 200             # 多少个batch保存一次checkpoint
trainRatio = 0.8           # 训练率

learningRateBase = 0.001
learningRateDecayStep = 500
learningRateDecayRate = 0.95


class POEMS:
    "poem class"
    def __init__(self, filename, isEvaluate=False):
        """预处理"""
        poems = []
        file = open(filename, "rb")
        for line in file:  # 每行都是一首诗
            title, author, poem = line.decode().strip().split("::")  # 获取诗的题目、作者、内容
            poem = poem.replace(' ','')
            if len(poem) < 10:  # 过滤掉比较短的诗
                continue
            poem = '[' + poem + ']' #为每个诗添加前后标志，以便机器识别
            poems.append(poem)
        # 计算字频
        wordFreq = collections.Counter()
        for poem in poems:
            wordFreq.update(poem)

        # 按照字频排序
        wordFreq[" "] = -1
        wordPairs = sorted(wordFreq.items(), key = lambda x: -x[1])
        self.words, freq = zip(*wordPairs)
        self.wordNum = len(self.words)

        self.wordToID = dict(zip(self.words, range(self.wordNum)))
        poemsVector = [([self.wordToID[word] for word in poem]) for poem in poems]
        if isEvaluate:
            self.trainVector = poemsVector[:int(len(poemsVector) * trainRatio)]
            self.testVector = poemsVector[int(len(poemsVector) * trainRatio):]
        else:
            self.trainVector = poemsVector
            self.testVector = []
        print("我的老师{}一共有{}首诗词".format(poet, len(self.trainVector)))


    def generateBatch(self, isTrain=True):
        if isTrain:
            poemsVector = self.trainVector
        else:
            poemsVector = self.testVector

        random.shuffle(poemsVector)
        batchNum = (len(poemsVector) - 1) // batchSize
        X = []
        Y = []
        # 构建训练batch
        for i in range(batchNum):
            batch = poemsVector[i * batchSize: (i + 1) * batchSize]
            maxLength = max([len(vector) for vector in batch])
            temp = np.full((batchSize, maxLength), self.wordToID[" "], np.int32)
            for j in range(batchSize):
                temp[j, :len(batch[j])] = batch[j]
            X.append(temp)
            temp2 = np.copy(temp)
            temp2[:, :-1] = temp[:, 1:]
            Y.append(temp2)
        return X, Y


class MODEL:
    """核心模型"""
    def __init__(self, trainData):
        self.trainData = trainData

    def buildModel(self, wordNum, gtX, hidden_units = 128, layers = 2):
        """搭建网络"""
        with tf.variable_scope("embedding"):
            embedding = tf.get_variable("embedding", [wordNum, hidden_units], dtype = tf.float32)
            inputbatch = tf.nn.embedding_lookup(embedding, gtX)
        basicCell = []
        for i in range(layers):
            basicCell.append(tf.nn.rnn_cell.LSTMCell(hidden_units, state_is_tuple = True))
        stackCell = tf.contrib.rnn.MultiRNNCell(basicCell, state_is_tuple = True)
        initState = stackCell.zero_state(np.shape(gtX)[0], tf.float32)
        outputs, finalState = tf.nn.dynamic_rnn(stackCell, inputbatch, initial_state = initState)
        outputs = tf.reshape(outputs, [-1, hidden_units])

        with tf.variable_scope("softmax"):
            w = tf.get_variable("w", [hidden_units, wordNum])
            b = tf.get_variable("b", [wordNum])
            logits = tf.matmul(outputs, w) + b

        probs = tf.nn.softmax(logits)
        return logits, probs, stackCell, initState, finalState

    def train(self, reload=True):
        """训练模型"""
        print('开始认真学习{}的诗篇...\n'.format(poet))
        gtX = tf.placeholder(tf.int32, shape=[batchSize, None])  # 定义输入
        gtY = tf.placeholder(tf.int32, shape=[batchSize, None])  # 定义输出

        logits, probs, a, b, c = self.buildModel(self.trainData.wordNum, gtX)

        targets = tf.reshape(gtY, [-1])

        #定义loss
        loss = tf.contrib.legacy_seq2seq.sequence_loss_by_example([logits], [targets],
                                                                  [tf.ones_like(targets, dtype=tf.float32)])
        globalStep = tf.Variable(0, trainable=False)
        addGlobalStep = globalStep.assign_add(1)

        cost = tf.reduce_mean(loss)
        trainableVariables = tf.trainable_variables()
        grads, a = tf.clip_by_global_norm(tf.gradients(cost, trainableVariables), 5) # 防止梯度爆炸
        learningRate = tf.train.exponential_decay(learningRateBase, global_step=globalStep,
                                                  decay_steps=learningRateDecayStep, decay_rate=learningRateDecayRate)
        optimizer = tf.train.AdamOptimizer(learningRate)
        trainOP = optimizer.apply_gradients(zip(grads, trainableVariables))

        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            saver = tf.train.Saver()

            if not os.path.exists(checkpointsPath):
                os.mkdir(checkpointsPath)

            if reload:
                checkPoint = tf.train.get_checkpoint_state(checkpointsPath)
                # 恢复checkpoint
                if checkPoint and checkPoint.model_checkpoint_path:
                    saver.restore(sess, checkPoint.model_checkpoint_path)
                    print("我先复习一下： %s\n" % checkPoint.model_checkpoint_path)
                else:
                    print("哎呀！之前好像没有学习这位诗人，我这就开始...\n")

            for epoch in range(epochNum):
                X, Y = self.trainData.generateBatch()
                epochSteps = len(X)
                for step, (x, y) in enumerate(zip(X, Y)):
                    a, loss, gStep = sess.run([trainOP, cost, addGlobalStep], feed_dict = {gtX:x, gtY:y})
                    print("epoch: %d, steps: %d/%d, loss: %3f" % (epoch + 1, step + 1, epochSteps, loss))
                    if gStep % saveStep == saveStep - 1: # 保存checkpoint
                        print("Saving what I have learnt...\n")
                        print()
                        print('Study makes me happy, go on...')
                        saver.save(sess, os.path.join(checkpointsPath, poet), global_step=gStep)

    def probsToWord(self, weights, words):
        """输出概率对应到字"""
        prefixSum = np.cumsum(weights)
        ratio = np.random.rand(1)
        index = np.searchsorted(prefixSum, ratio * prefixSum[-1]) # 输出概率大的字对应的区间大，被选择的概率也大
        return words[index[0]]

    def test(self):
        """自由作诗"""
        print('正在模仿{}为你写诗...\n'.format(poet))
        gtX = tf.placeholder(tf.int32, shape=[1, None])
        logits, probs, stackCell, initState, finalState = self.buildModel(self.trainData.wordNum, gtX)
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            saver = tf.train.Saver()
            checkPoint = tf.train.get_checkpoint_state(checkpointsPath)
            # 恢复checkpoint
            if checkPoint and checkPoint.model_checkpoint_path:
                saver.restore(sess, checkPoint.model_checkpoint_path)
            else:
                print("额，貌似我还没有学习这位诗人鸭！\n")
                exit(1)

            poems = []
            # 生成generateNum这么多首诗，每首诗以左中括号开始，以右中括号或空格结束，每次生成的prob用probsToWord方法转成字。
            for i in range(generateNum):
                state = sess.run(stackCell.zero_state(1, tf.float32))
                x = np.array([[self.trainData.wordToID['[']]])
                probs1, state = sess.run([probs, finalState], feed_dict={gtX: x, initState: state})
                word = self.probsToWord(probs1, self.trainData.words)
                poem = ''
                sentenceNum = 0
                while word not in [' ', ']']:
                    poem += word
                    if word in ['。', '？', '！', '，']:
                        sentenceNum += 1
                        if sentenceNum % 2 == 0:
                            poem += '\n'
                    x = np.array([[self.trainData.wordToID[word]]])
                    probs2, state = sess.run([probs, finalState], feed_dict={gtX: x, initState: state})
                    word = self.probsToWord(probs2, self.trainData.words)
                poems.append(poem)
                output(poem)
            return poems

    def testHead(self, characters):
        """藏头诗"""
        gtX = tf.placeholder(tf.int32, shape=[1, None])
        logits, probs, stackCell, initState, finalState = self.buildModel(self.trainData.wordNum, gtX)
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            saver = tf.train.Saver()
            checkPoint = tf.train.get_checkpoint_state(checkpointsPath)
            # 恢复训练数据
            if checkPoint and checkPoint.model_checkpoint_path:
                saver.restore(sess, checkPoint.model_checkpoint_path)
            else:
                print("额，貌似我还没有学习这位诗人鸭！\n")
                exit(1)
            flag = 1
            endSign = {-1: "，", 1: "。"}
            poem = ''
            state = sess.run(stackCell.zero_state(1, tf.float32))
            x = np.array([[self.trainData.wordToID['[']]])
            probs1, state = sess.run([probs, finalState], feed_dict={gtX: x, initState: state})
            for word in characters:
                if self.trainData.wordToID.get(word) == None:
                    print("小人才疏学浅，江郎才尽呀！")
                    exit(0)
                flag = -flag
                while word not in [']', '，', '。', ' ', '？', '！']:
                    poem += word
                    x = np.array([[self.trainData.wordToID[word]]])
                    probs2, state = sess.run([probs, finalState], feed_dict={gtX: x, initState: state})
                    word = self.probsToWord(probs2, self.trainData.words)

                poem += endSign[flag]
                # 更新state
                if endSign[flag] == '。':
                    probs2, state = sess.run([probs, finalState],
                                             feed_dict={gtX: np.array([[self.trainData.wordToID["。"]]]), initState: state})
                    poem += '\n'
                else:
                    probs2, state = sess.run([probs, finalState],
                                             feed_dict={gtX: np.array([[self.trainData.wordToID["，"]]]), initState: state})

            output(poem)
            return poem


def output(poem):
    '''美化输出格式'''
    poem = poem.strip('\n')
    lenth = len(poem.split('\n')[0])*2 + 8
    print()
    print('-'*lenth)
    print()
    for i in poem.split('\n'):
        print('     '+i)
    print()
    print('-'*lenth)
    print()

def defineArgs():
    """定义传入参数"""
    parser = argparse.ArgumentParser(description = "Chinese_poem_generator.")
    parser.add_argument("-m", "--mode", help = "select mode by 'train' or test or head",
                        choices = ["train", "test", "head"], default = "test")
    parser.add_argument("-p", "--poet", type=str, default = '李白', help =" 选择诗人",
                        choices = ['李白', '杜甫', '苏轼', '辛弃疾', '白居易', '陆游', '杨万里', '刘克庄', '王安石', '黄庭坚'])
    return parser.parse_args()

if __name__ == "__main__":
    os.environ['CUDA_VISIBLE_DEVICES'] = "0"
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    args = defineArgs()
    poet = args.poet
    trainPoems = "./dataset/" + poet + "/" + poet + ".txt" # 训练数据集目录
    checkpointsPath = "./checkpoints/" + poet # checkpoints存放位置

    trainData = POEMS(trainPoems)
    Totoro = MODEL(trainData)

    if args.mode == "train":
        Totoro.train()
    else:
        if args.mode == "test":
            poems = Totoro.test()
        else:
            print('我学习{}的作品比较少，你不要为难我呀！'.format(poet))
            characters = input("请指教：")
            poems = Totoro.testHead(characters)
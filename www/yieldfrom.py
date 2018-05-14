#! -*- coding: utf-8 -*-
'''
这段代码从一个字典中读取男生和女生的身高和体重。然后把数据传给之前定义的 averager 协程，最后生成一个报告。
执行结果为
6 boys  averaging 54.00kg
6 boys  averaging 1.68m
6 girls averaging 44.00kg
6 girls averaging 1.58m
'''
from collections import namedtuple
import  time
from datetime import datetime

Result = namedtuple('Result', 'count average')

# 子生成器  运行时，有4个generator实例
# 这个例子和上边示例中的 averager 协程一样，只不过这里是作为子生成器使用
def averager():
    total = 0.0
    count = 0
    average = None
    time.sleep(3)
    while True:
        # main 函数发送数据到这里
        term = yield
        if term is None: # 终止条件
            break
        total += term
        count += 1
        average = total/count

    return Result(count, average) # 返回的Result 会成为grouper函数中yield from表达式的值


# 委派生成器

def grouper(results, key):
     # 这个循环每次都会新建一个averager 实例，每个实例都是作为协程使用的生成器对象
    while True:
        # grouper 发送的每个值都会经由yield from 处理，通过管道传给averager 实例。grouper会在yield from表达式处暂停，等待averager实例处理客户端发来的值。averager实例运行完毕后，返回的值绑定到results[key] 上。while 循环会不断创建averager实例，处理更多的值。
        results[key] = yield from averager()
        print(averager())


# 调用方
def main(data):
    a = datetime.now()
    results = {}
    for key, values in data.items():
        # group 是调用grouper函数得到的生成器对象，传给grouper 函数的第一个参数是results，用于收集结果；第二个是某个键
        group = grouper(results, key)
        print(group)
        next(group)
        for value in values:
            # 把各个value传给grouper 传入的值最终到达averager函数中；
            # grouper并不知道传入的是什么，同时grouper实例在yield from处暂停
            group.send(value)
        # 把None传入groupper，传入的值最终到达averager函数中，导致当前实例终止。然后继续创建下一个实例。
        # 如果没有group.send(None)，那么averager子生成器永远不会终止，委派生成器也永远不会在此激活，也就不会为result[key]赋值
        group.send(None)
    b = datetime.now()
    print((b-a).seconds)
    report(results)


# 输出报告
def report(results):
    for key, result in sorted(results.items()):
        group, unit = key.split(';')
        print('{:2} {:5} averaging {:.2f}{}'.format(result.count, group, result.average, unit))


data = {
    'girls;kg':[40, 41, 42, 43, 44, 54],
    'girls;m': [1.5, 1.6, 1.8, 1.5, 1.45, 1.6],
    'boys;kg':[50, 51, 62, 53, 54, 54],
    'boys;m': [1.6, 1.8, 1.8, 1.7, 1.55, 1.6],
}

if __name__ == '__main__':
    main(data)
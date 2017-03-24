

# 0x00 前言

最近muhe师傅，给我发了一个PDF，是湾湾写的二进制自动化分析攻击，他的文档主要写的上angr，于是玩对这个玩意儿也开始有了一点兴趣。刚好假期joekr师傅给我发了一个angr分析的二进制题目。于是2333 就开始了折腾。
# 什么是angr
angr是一个用于分析二进制文件的python框架。它专注于静态和符号分析，使其适用于各种任务。其项目地址是，[https://github.com/angr](https://github.com/angr).


# 什么是符号执行

*来自维基百科*
符号执行 （Symbolic Execution）是一种程序分析技术。其可以通过分析程序来得到让特定代码区域执行的输入。使用符号执行分析一个程序时，该程序会使用符号值作为输入，而非一般执行程序时使用的具体值。在达到目标代码时，分析器可以得到相应的路径约束，然后通过约束求解器来得到可以触发目标代码的具体值。[1]
符号模拟技术（symbolic simulation）则把类似的思想用于硬件分析。符号计算（Symbolic computation）则用于数学表达式分析。

# angr安装 以及遇到的坑
我这使用的是ubutnu系统：
## 安装依赖
```bash
sudo apt-get install python-dev libffi-dev build-essential virtualenvwrapper
```
如果你正在尝试angr管理，你会需要安装
```bash
sudo apt-get install libqt4-dev graphviz-dev
```
## 创建虚拟环境以及安装angr模块
`mkvirtualenv angr && pip install angr`通常应该足够在大多数情况下安装angr，因为angr发布在Python包索引上。
Fish（shell）用户可以使用virtualfish或virtualenv包。
`vf new angr && vf activate angr && pip install angr`

## 遇到的坑
> 由于在导入angr时加载capstone失败导致的ImportError

官方文档仔细介绍了如何几种常见的错误报告，我这里遇到的是上面的这种。解决方法有两种：
1. pip install -I --no-use-wheel capston
2. 移动libcapstone.so到与Python文件相同的目录


# angr简单使用
## 装载二进制文件
```py
>>> import angr

>>> b = angr.Project("/binnary/")   # 这里放的是bin的路径
```
更多详细的东西，我就不当搬运工了，可以转[https://docs.angr.io/docs/loading.html](https://docs.angr.io/docs/loading.html)
# angr脚本
如果上一个标题的内容，即angr框架的基本用法，那么我们就可以开始学习一下angr的运用，以及脚本的编写。
*YSC* 整理了angr比较常用的方法：
- Surveyours
- Path group
- Symbolic args
- Symbolic input
- Breakpoint
- Hook
## Surveyours
Surveyor是驱动符号执行的引擎：它跟踪哪些路径处于活动状态，标识哪些路径向前转，哪些路径要修剪，并优化资源的分配。
但是在官方文档的介绍当中，他是更加推荐的是使用*PathGroups*的使用。
最基本的，我们可以这样使用他
### Explorer
`angr.surveyor.Explore`是`Surveyor`实现符号执行的一个方法。它将实现起点，目标，过滤等功能，以及确定执行的路径避免陷入无谓的循环当中。
```py
import angr
b =  angr.Project("./examples/Bin") # 第一就是基本的载入二进制文件

e =  b.surveyor.Explore()
print e.step() # 暂停

print e.run() # 开始
print "%d paths are still running" % len(e.active)
print "%d paths are backgrounded due to lack of resources" % len(e.spilled)
print "%d paths are suspended due to user action" % len(e.suspended)
print "%d paths had errors" % len(e.errored)
print "%d paths deadended" % len(e.deadended)
```
上面的脚本并没有做任何简单的限制，因此，想必任务量是极其大的，因此，我们可以做一些条件。
```py
import angr
e = b.surveyors.Explorer(find=(0x4006ed,), avoid=(0x4006aa,0x4006fd))
e.run()
if len(e.found) > 0:
  print "Found backdoor path:", e.found[0]
 print "Avoided %d paths" % len(e.avoided)

 print e.found[ 0 ].state.se._solver.result.model
 ```
 Explorer这个方法可以设定说要找到哪个程式执行的位址，可以用find=(addr1)来找，和使用avoid=(addr2)来避免找到某位址。设定find=(addr1)有点像是在下断点，但注意位址必须是基本区块（basic block）的开头 ，否则angr并不会找到该位址，导致最后该路径会被归类成deadended而不是found。
 其中se代表求解器solver engine的意思。

### Path group
我查阅了官方文档给的出的CTF 题目解决样例，发现基本都是使用Path group这个方法的。仔细对比了一下，这个方法和surveyors很相像，但是多出了像state等参数。
```py
import angr

p =  angr.Project("./examples/Bin")

s =  p.factory.blank_state(addr = 0x4006ed)
pg = p.factory.Path_group(s,immutable = False)
path = pg.explore(find  = (0x4006aa,))

print path
print pg.found[0].state.se._solver.result.model
```
上面的脚本，先是定义了一个变数s，其中一个blank_state代表的是空白的状态，起点的设定是从0x4006ed开始（我们通过这样的设置，让程序从我们指定的位置开始）至于如果要从头开始执行，可以用s = prog.factory.entry_state(args=["./vul"])来指定在程式进入点时的状态。

紧接着的就是path_group，刚刚的状态放进去当参数即可，接下来则和surveyors相同。

# CodeGateCTF - Angrybird
上面的内容，都是基本设计到了angr的使用，这里我们用一个刚结束没多久的比赛CodeGateCTF的一个题目作为demo，我们尝试自己分析并且编写一下脚本。题目连接在文章最后会提供。
## 分析
![](http://oayoilchh.bkt.clouddn.com/17-3-8/19641798-file_1488964129720_e314.png)




0 0 当我看到这个东西的时候，我是很想骂人的。我总不能一个一个去patch这些该死的东西吧。
我们最终的结果，肯定是要得到flag，得到flag，我们肯定得调用print 或者put这样的函数，那么通过静态分析，我们很可以很容易找到目标地址。

![](http://oayoilchh.bkt.clouddn.com/17-3-8/14931392-file_1488964126794_3a4f.png)
这里，目标地址就是0000000000404FC1。
那么，我们如何避免那些该死的东西呢，我们这里可以设置aovid函数，我们可以设置一个简单的入口。或者，我们干脆一点，把一些无用的东西nop掉。这里，我选择选择设置入口
## 脚本
```python
import angr

main = 0x4007DA
find = 0x404FBC
avoid = [0x400590]

p = angr.Project('./angrybird2')
init = p.factory.blank_state(addr=main)
pg = p.factory.path_group(init, threads=8)
ex = pg.explore(find=find, avoid=avoid)

final = ex.found[0].state
flag = final.posix.dumps(0)

print("Flag: {0}".format(final.posix.dumps(1)))
```

# 参考文档以及链接
angr 官方文档 [doc](https://docs.angr.io/docs)
angr脚本编写参考 [Ysc'blog](http://ysc21.github.io/)
CodeGateCTF - Angrybird [Angrybird](https://github.com/ctfs/write-ups-2017/tree/master/codegate-prequals-2017/re/angrybird-500)


#　以及最后
虽然angr很好用，但是我们也不能执着用工具，方法还是要学习的，比如，我师傅让我好好学习一下angr的代码。

# Moment-Likes-Collecting-Helper

朋友圈集赞小助手，现已完整适配微信浅色、深色模式

## Requirements

```bash
pip install requests flet numpy PIL Pillow opencv-python
```

## 局限性

1. 因为按照绝对分辨率进行定位，目前仅对分辨率1080*（2300~2500）这一范围内的截图支持良好，宽度不同于1080px必然会导致错误，长度不在上述区间内可能会导致生成效果不好

2. 因为使用了过多的库，打包后的程序体量较大，运行速度慢
3. 头像爬虫的选择性较小，秉持着不能把别人家服务器给爬崩了的原则，爬虫引入sleep机制，速度较慢

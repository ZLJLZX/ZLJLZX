# 主页素材说明 · About these files

这个文件夹是生成主页图片（横幅、爱好卡片、页脚）的脚本，平时不用管它。

## 修改横幅或卡片上的文字

1. 打开 `tools/build.py`，修改最上面 `CONTENT` 部分：名字、打字动画里循环的句子、爱好卡片的文字。
2. 在仓库根目录运行：

   ```bash
   pip install fonttools uharfbuzz
   python tools/build.py
   ```

   第一次运行会自动下载开源字体（Nunito、Noto Sans SC，约 30 MB，SIL Open Font License）。
3. 把 `assets/` 里更新后的 `.svg` 上传覆盖即可。

每张图都有浅色（`-light`）和深色（`-dark`）两个版本，README 会按访客的 GitHub 主题自动显示对应的一张。

## 打开统计卡片（预留功能）

等提交多起来以后，可以在主页加上自动更新的统计卡片：

1. 把 `tools/stats-workflow.yml` 移动到 `.github/workflows/stats.yml`。
2. 打开仓库的 **Actions** 页面，选择 “Update stats cards”，点 **Run workflow** 运行一次。之后它每天自动更新。
3. 编辑 `README.md`，删掉 “预留：GitHub 统计卡片” 那一行和 “预留段落结束” 那一行，卡片就会显示出来。

卡片是透明背景，浅色、深色主题下都能看清；默认隐藏了等级评分。

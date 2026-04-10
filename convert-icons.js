// convert-icons.js
// 将 frontend/images/*.svg 全部转成 PNG（40×40 TabBar 图标，81×81 分类图标）
// 使用方法：node convert-icons.js

const sharp = require('sharp')
const fs = require('fs')
const path = require('path')

const imagesDir = path.join(__dirname, 'frontend', 'images')

// 转换规则：{ file: 'xxx.svg', size: 40|81 }
const files = fs.readdirSync(imagesDir).filter(f => f.endsWith('.svg'))

async function convert(svgFile, size) {
  const svgPath = path.join(imagesDir, svgFile)
  const pngPath = path.join(imagesDir, svgFile.replace('.svg', '.png'))
  const svgBuffer = fs.readFileSync(svgPath)

  await sharp(svgBuffer)
    .resize(size, size)
    .png()
    .toFile(pngPath)

  console.log(`✅ ${svgFile} → ${svgFile.replace('.svg', '.png')} (${size}×${size})`)
}

async function run() {
  for (const f of files) {
    // tab-*.svg → 40×40（微信 tabBar 推荐 81rpx，换算约 40px）
    // category-*.svg → 81×81
    const size = f.startsWith('category-') ? 81 : 40
    try {
      await convert(f, size)
    } catch (e) {
      console.error(`❌ ${f}: ${e.message}`)
    }
  }
  console.log('\n所有图标转换完成！')
}

run()

// scripts/convert-webp.js
// 批量将 backend/static/images 中的 JPG/PNG 转化为 WebP
// 使用方法：node scripts/convert-webp.js

const sharp = require('sharp')
const fs = require('fs')
const path = require('path')

const targetDir = path.join(__dirname, '..', 'backend', 'static', 'images')

if (!fs.existsSync(targetDir)) {
  console.error('❌ 找不到后端图片目录:', targetDir)
  process.exit(1)
}

const files = fs.readdirSync(targetDir).filter(f => /\.(jpg|jpeg|png)$/i.test(f))

async function run() {
  console.log(`🚀 开始转换 ${files.length} 张图片...`)
  let count = 0
  
  for (const f of files) {
    const inputPath = path.join(targetDir, f)
    const outPath = path.join(targetDir, f.replace(/\.(jpg|jpeg|png)$/i, '.webp'))
    
    try {
      if (fs.existsSync(outPath)) {
        console.log(`⏩ 跳过已存在的: ${f}`)
        continue
      }
      
      await sharp(inputPath)
        .webp({ quality: 85 })
        .toFile(outPath)
      
      count++
      console.log(`✅ 已转换: ${f} -> webp`)
    } catch (e) {
      console.error(`❌ 转换失败 ${f}:`, e.message)
    }
  }
  
  console.log(`\n🎉 转换完成！新增了 ${count} 张 WebP 图片。`)
}

run()

# Bazo — Frontend (كامل)

React + Vite + TypeScript + Tailwind v4. Build نظيف (102 module، صفر أخطاء)، Docker جاهز.

## ✅ كل الصفحات (12 صفحة)

الرئيسية، دخول/تسجيل، بحث، تفاصيل منتج، إنشاء إعلان (AI برفع صور فعلي + يدوي)، **مراجعة/تعديل مسودة (حقول ديناميكية حسب الفئة)**، إعلاناتي، المفضلة، الرسائل، و**لوحة إدارة كاملة** (نظرة عامة، مستخدمين، إعلانات، فئات).

## التشغيل

### Docker
```bash
docker compose up --build   # من مجلد ai-marketplace/ الجذر
```

### محلياً
```bash
npm install
cp .env.example .env
npm run dev       # http://localhost:5173
npm run build      # فحص نهائي: npm run build يجب يعطي صفر أخطاء
```

## الناقص المتبقي (صراحة)

- صفحة ملف بائع عام (/seller/:id)
- Tests (Vitest + Testing Library)
- تحرير attributes_schema من لوحة الإدارة (حالياً فئات جديدة بدون حقول مخصصة)
- Loading/error states أدق ببعض الأماكن

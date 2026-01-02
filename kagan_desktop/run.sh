#!/bin/bash
# اسکریپت اجرای Kagan Desktop ERP

echo "=================================="
echo "�� Kagan Desktop ERP"
echo "=================================="
echo ""

# بررسی Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python نصب نیست!"
        echo "لطفاً Python 3.9 یا بالاتر نصب کنید."
        exit 1
    else
        PYTHON_CMD=python
    fi
else
    PYTHON_CMD=python3
fi

# نمایش نسخه Python
echo "✅ Python یافت شد:"
$PYTHON_CMD --version
echo ""

# اجرای برنامه
echo "🚀 در حال اجرای برنامه..."
echo ""
$PYTHON_CMD main.py

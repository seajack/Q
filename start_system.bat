@echo off
echo 🚀 启动工作流可视化设计器系统
echo =====================================

echo.
echo 📊 检查系统状态...
python system_status_check.py

echo.
echo 🔧 启动后端服务...
start "Django Backend" cmd /k "cd /d e:\code\Q\org-platform\backend && python manage.py runserver 0.0.0.0:8001"

echo.
echo 等待后端服务启动...
timeout /t 3 /nobreak > nul

echo.
echo 🎨 启动前端服务...
start "Vue Frontend" cmd /k "cd /d e:\code\Q\org-platform\frontend && npm run dev"

echo.
echo ⏳ 等待服务启动完成...
timeout /t 5 /nobreak > nul

echo.
echo 🌐 访问地址:
echo   前端应用: http://localhost:5173
echo   后端API: http://localhost:8001
echo   工作流管理: http://localhost:5173/workflow-list
echo   流程设计器: http://localhost:5173/workflow-designer
echo   智能分析: http://localhost:5173/intelligent-analysis

echo.
echo 🎉 系统启动完成！
echo 按任意键打开浏览器...
pause > nul

start http://localhost:5173

echo.
echo 系统正在运行中...
echo 关闭此窗口将停止所有服务
pause

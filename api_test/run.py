import os
import pytest

if __name__ == '__main__':
    # 清空旧报告
    os.system("rd /s /q reports\\allure_raw")
    # 执行用例
    pytest.main()
    # 打开报告
    os.system("allure generate reports/allure_raw -o reports/allure_html --clean")
    os.system("allure open reports/allure_html")

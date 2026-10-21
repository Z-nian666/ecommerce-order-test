pip install -r requirements.txt
pytest api_test/testcases/ --alluredir=api_test/reports/allure-results
allure serve api_test/reports/allure-results

from time import sleep
from helium import *
from selenium.webdriver.common.by import By
import time
from threading import Thread
from selenium.webdriver.common.action_chains import ActionChains
#email = "iansooamazonuk@gmail.com"
#passwd = "Lifeisgreat5!"
#email = "surawadeesoo1@gmail.com"
#passwd = "Bangkok101!"

drives = {}

def login_site(op,uname,password):
    set_driver(op)
    print("start")
    url = "https://traders.td365.com/login"
    go_to(url)
    op.find_element_by_tag_name('body').screenshot("start.png")
    wait_until(Button('Log in').exists)
    print(1)
#    op.find_element_by_tag_name('body').screenshot("s1.png")
    op = helium.get_driver()
    username_field = op.find_element_by_id("login_userid")
    pass_field = op.find_element_by_id("login_password")
    write(uname,into=username_field)
    write(password,into=pass_field)
    op.find_element_by_tag_name('body').screenshot("s1.png")
    click("Log in")
    print(2)
    op.find_element_by_tag_name('body').screenshot("s2.png")
    wait_until(Button('Launch').exists)
    click("Launch")
    i = 0
    while i < 1:
        d = find_all(Window())
        if len(d) > 1:
            i = 1
    switch_to(find_all(Window())[1])
    print(3)
    #op.find_element_by_tag_name('body').screenshot("s3.png")
    #op_new = helium.Window()
    print(op.current_url)
    return 0


def place_trade(op,inst,quantity,trade_type,trail):
    global drives
    #op.implicitly_wait(2)
    start_time = time.time()
    
    op.find_element_by_id("txtSearchMarket").click()
    op.find_element_by_id("txtSearchMarket").clear()
    op.find_element_by_id("txtSearchMarket").send_keys(inst)
    f = 0
    while f < 1:
        
        results = op.find_elements_by_class_name("yui-dt-col-MarketName")
        for result in results:
            reses = (result.find_elements_by_class_name("yui-dt-liner"))
            for res in reses:
                if res.text == inst:
                    td_but = res.find_element_by_xpath("..").find_element_by_xpath("..")
                    try:
                       td_but.find_element_by_tag_name("span").click()
                    except:
                       pass
                    f = 2
    print("here")
    h = 0
    hedges = []
    while h < 1:
      hedges = op.find_elements_by_class_name("hedging-field")
      #print(hedges)
      if len(hedges) > 0:
            h = 2
    stakes = []
    print("there")
    s = 0
    while s < 1:
        print(s)
        stakes = op.find_elements_by_class_name("txtStake")
        print(stakes)
        if len(stakes) > 0:
            ssos = 0
            for stake in stakes:
                while ssos < 1:
                    stake_status = stake.is_displayed()
                    if stake_status is True:
                        ssos = 2
                ActionChains(op).move_to_element(stake).click(stake).perform()
                stake.clear()
                stake.send_keys(quantity)
                s = 2

    end_time = time.time()
    print("--- %s seconds ---" % (end_time- start_time))
    alert_control = op.find_element_by_class_name("ticket-controls")
    close_but = alert_control.find_element_by_class_name("close")
    ActionChains(op).move_to_element(close_but).click(close_but).perform()
    return
    side_b = op.find_element_by_class_name("btn-sell")
    ActionChains(op).move_to_element(side_b).click(side_b).perform()

from selenium.webdriver.chrome.options import Options
#chrome_options = Options()
#chrome_options.add_argument("--headless")
#chrome_options.add_argument('--no-sandbox')

for user in users:
  try:
    print(user[0],user[1])
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    driver = start_chrome(options= chrome_options)
    print(123)
    drives[user[0]] = driver
    print(1234)
    login_site(driver,user[0],user[1])
  except Exception as e:
    print(str(e))
    kill_browser()

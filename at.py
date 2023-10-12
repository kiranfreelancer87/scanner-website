from time import sleep
from helium import *
from selenium.webdriver.common.by import By
from time import sleep

#email = "iansooamazonuk@gmail.com"
#passwd = "Lifeisgreat5!"
email = "surawadeesoo1@gmail.com"
passwd = "Bangkok101!"
users = [["surawadeesoo1@gmail.com", "Bangkok101!"],[ "iansooamazonuk@gmail.com","Lifeisgreat5!"]]
#driver = start_chrome(url=url,headless=False)


def login_site(op,uname,password):
    set_driver(op)
    url = "https://traders.td365.com/login"
    go_to(url)
    wait_until(Button('Log in').exists)
    print(1)
    op.find_element_by_tag_name('body').screenshot("s1.png")
    #op = helium.get_driver()
    username_field = op.find_element_by_id("login_userid")
    pass_field = op.find_element_by_id("login_password")
    write(uname,into=username_field)
    write(password,into=pass_field)
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
    
def place_trade(inst,quantity,trade_type,trail):
    global driver
    wait_until(Text("Current Margin").exists)
    print(11)
    op = get_driver()
    op.find_element_by_tag_name('body').screenshot("s11.png")
    search = op.find_element_by_id("txtSearchMarket")
    write(inst, into=search)
    sleep(2)
    click("TRADE")
    print(22)
    op.find_element_by_tag_name('body').screenshot("ss22.png")
    wait_until(Text("Stop / Limit »").exists)
    ip_fields = find_all(TextField("", below="Amount"))
    for ip_field in ip_fields:
        #print(ip_field)
        write(quantity,into=ip_field)
    click(trade_type)
    click("Stop / Limit »")
    click("Trailing")
    press(TAB)
    press(trail)
    #click("SUBMIT")
    op.find_element_by_tag_name('body').screenshot("ss.png")
    refresh()

from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
driver = start_chrome(options= chrome_options)

#from selenium.webdriver.firefox.options import Options as FirefoxOptions
#fr_options = FirefoxOptions()
#fr_options.headless = True
#driver = start_chrome(headless=True)
#driver = start_firefox(headless=True)
for user in users:
  try:
    driver = start_chrome(options= chrome_options)
    login_site(driver,email,passwd)
  except Exception as e:
    print(str(e))
    kill_browser()

#quantity = "0.5"
#trade_type = "Buy"
#item = "US 2000 - Rolling Cash"
#item = "GBP/AUD - Rolling Spot"
#trail = "5"
#try:
 #pass
 #place_trade(driver,item,quantity, trade_type, trail)
#except Exception as e:
 #   print(str(e))
  #  kill_browser

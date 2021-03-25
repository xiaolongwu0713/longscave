import time
import qrcode
import os
from flask import Flask, render_template, current_app, request
import flask
from app.teaching import bp
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


@bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('/teaching/index.html')


@bp.route('/success', methods=['GET', 'POST'])
def pay_success():
    return render_template('/alipay/pay_result_success.html')


@bp.route('/timeout', methods=['GET', 'POST'])
def timeout():
    return render_template('/alipay/pay_result_timeout.html')


@bp.route('/canceled', methods=['GET', 'POST'])
def canceled():
    return render_template('/alipay/canceled.html')


def init_alipay_cfg(env):
    '''
    初始化alipay配置
    :return: alipay 对象
    '''
    env = env
    if env == "prd":
        alipay = AliPay(
            appid=current_app.config['APP_ID_PRD'],
            app_notify_url='http://hd5ckg.natappfree.cc/call_back.html',
            alipay_public_key_string=open(current_app.config['ALIPAY_PUBLIC_KEY_PATH_PRD']).read(),
            app_private_key_string=open(current_app.config['APP_PRIVATE_KEY_PATH_PRD']).read(),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=False  # False: production env. True: sandbox env
        )
    elif env == "test":
        alipay = AliPay(
            appid=current_app.config['APP_ID_TEST'],
            app_notify_url='http://hd5ckg.natappfree.cc/call_back.html',
            alipay_public_key_string=open(current_app.config['ALIPAY_PUBLIC_KEY_PATH_TEST']).read(),
            app_private_key_string=open(current_app.config['APP_PRIVATE_KEY_PATH_TEST']).read(),
            sign_type="RSA",  # RSA 或者 RSA2
            debug=True  # False: production env. True: sandbox env
        )
    return alipay


@bp.route('/show_qr/<env>/<product>/<int:amount>', methods=['GET','POST'])
def show_qr(env, product, amount):
    subject = product
    amount = amount
    env = env
    qrcode_file_name, out_trade_no = qr_generator(env, product, amount)
    if env == 'test':
        return render_template('alipay/show_qr_test.html', subject=subject, amount=amount, qrcode_file_name=qrcode_file_name, env=env, out_trade_no=out_trade_no)
    elif env == 'prd':
        return render_template('alipay/show_qr_prd.html', subject=subject, amount=amount, qrcode_file_name=qrcode_file_name, env=env, out_trade_no=out_trade_no)


def qr_generator(env, product, amount):
# @bp.route('/show_qr', methods=['GET','POST'])
    subject = product
    amount = amount
    env = env
    out_trade_no_time = int(time.time())
    out_trade_no = str(product) + str(out_trade_no_time)

    myalipay = init_alipay_cfg(env)
    result = myalipay.api_alipay_trade_precreate(
        subject=product,
        out_trade_no=out_trade_no,
        total_amount=amount)
    print('返回值：', result)
    code_url = result.get('qr_code')
    if not code_url:
        print("no qr_code returned")
        print(result.get('预付订单创建失败：', 'msg'))
        return "failed to connect to Alipay server"
    else:
        qrcode_img = qr_img_generator(code_url, subject, out_trade_no, env)
        filename = str("qrcodeimg") + str(env) + str(subject) + str(out_trade_no) + str(".png")
        if env == 'prd':
            outputfile = os.path.join(os.getcwd(), 'app/static/img/alipay_qr/prd/', filename)
        elif env == 'test':
            outputfile = os.path.join(os.getcwd(), 'app/static/img/alipay_qr/test/', filename)
        qrcode_img.save(outputfile)
        print('二维码保存成功！')
        qrcode_file_name = os.path.basename(outputfile)
        # return code_url
    return qrcode_file_name, out_trade_no


def qr_img_generator(code_url, subject, out_trade_no, env):
    '''
    生成二维码
    :return None
    '''
    # print(code_url)
    env = env
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=1
    )
    qr.add_data(code_url)  # 二维码所含信息
    img = qr.make_image()  # 生成二维码图片
    return img


@bp.route('/query_order/', methods=['GET','POST'])
def query_order():
    #env = env
    out_trade_no = str(request.form['out_trade_no'])
    env = str(request.form['env'])
    print(env)
    print(out_trade_no)
    for i in range(15):
        print ("sleep 2 secs")
        time.sleep(2)
        result = init_alipay_cfg(env).api_alipay_trade_query(out_trade_no=out_trade_no)
        print(result)
        if result.get("code") == "40004" and result.get("sub_code") == "ACQ.TRADE_NOT_EXIST":
            print('trade not exist!')
            print('Please scan QR image')
            #return 'canceled'
        elif result.get("code") == "10000" and result.get("trade_status") == "WAIT_BUYER_PAY":
            print("Waiting to pay.....")
        elif result.get("code") == "10000" and result.get("trade_status") == "TRADE_SUCCESS":
            print('Order paied!')
            print('order status：', result)
            return 'paied'
    print("time out")
    cancel_order(out_trade_no, env)
    return 'timeout'


@bp.route('/test_query_order/', methods=['GET','POST'])
def test_query_order():
    out_trade_no = str(request.form['out_trade_no'])
    env = str(request.form['env'])
    print(env)
    print(out_trade_no)
    for i in range(30):
        print("sleep 2 seconds")
        time.sleep(2)
        result = init_alipay_cfg(env).api_alipay_trade_query(out_trade_no=out_trade_no)
        print(result)


def cancel_order(out_trade_no, env):
    """
    撤销订单
    :param out_trade_no:
    :param cancel_time: 撤销前的等待时间(若未支付)，撤销后在商家中心-交易下的交易状态显示为"关闭"
    :return:
    """
    result = init_alipay_cfg(env).api_alipay_trade_cancel(out_trade_no=out_trade_no)
    print('取消订单返回值：', result)
    resp_state = result.get('msg')
    # print(resp_state)
    action = result.get('action')
    # print(action)
    if resp_state == 'Success':
        print("canceled successfully")
        '''
        if action == 'close':
            print("30秒内未支付订单，订单已被取消！")
        elif action == 'refund':
            print('该笔交易目前状态为：', action)
        '''
        return 1
    else:
        print('请求失败：', resp_state)
        return 2


def need_refund(out_trade_no, refund_amount, out_request_no):
    """
    退款操作
    :param out_trade_no: 商户订单号
    :param refund_amount: 退款金额，小于等于订单金额
    :param out_request_no: 商户自定义参数，用来标识该次退款请求的唯一性,可使用 out_trade_no_退款金额*100 的构造方式
    :return:
    """
    result = init_alipay_cfg().api_alipay_trade_refund(out_trade_no=out_trade_no,
                                                       refund_amount=refund_amount,
                                                       out_request_no=out_request_no)

    if result["code"] == "10000":
        return result  # 接口调用成功则返回result
    else:
        return result["msg"]  # 接口调用失败则返回原因


def refund_query(out_request_no, out_trade_no):
    """
    退款查询：同一笔交易可能有多次退款操作（每次退一部分）
    :param out_request_no: 商户自定义的单次退款请求标识符
    :param out_trade_no: 商户订单号
    :return:
    """
    result = init_alipay_cfg().api_alipay_trade_fastpay_refund_query(out_request_no, out_trade_no=out_trade_no)

    if result["code"] == "10000":
        return result  # 接口调用成功则返回result
    else:
        return result["msg"]  # 接口调用失败则返回原因

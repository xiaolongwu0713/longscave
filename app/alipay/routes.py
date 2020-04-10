from alipay import AliPay
from app.alipay.forms import queryorderform
import time, qrcode
import os
from flask import Flask, render_template, current_app, request
import flask
from app.alipay import bp
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


@bp.route('/timer', methods=['GET', 'POST'])
def timer():
    return render_template('/alipay/timer.html')


@bp.route('/pay_success', methods=['GET', 'POST'])
def pay_success():
    return render_template('/alipay/pay_success.html')


@bp.route('/queryorder', methods=['GET', 'POST'])
def queryorder():
    form = queryorderform()
    if form.validate_on_submit():
        trade_number = form.order_number.data
        result = init_alipay_cfg().api_alipay_trade_query(out_trade_no=trade_number)
        return render_template('/alipay/queryorder.html',  form=form, result=result)
    return render_template('/alipay/queryorder.html',  form=form)


@bp.route('/canceled', methods=['GET', 'POST'])
def canceled():
    return render_template('/alipay/canceled.html')


def init_alipay_cfg():
    '''
    初始化alipay配置
    :return: alipay 对象
    '''
    env = "prd"
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


@bp.route('/show_qr/<product>/<int:amount>', methods=['GET','POST'])
def show_qr(product, amount):
# @bp.route('/show_qr', methods=['GET','POST'])
# def show_qr():
    #product = 'thing1111'
    #amount = 10.00
    subject = product
    amount = amount
    out_trade_no_time = int(time.time())
    out_trade_no = str(product) + str(out_trade_no_time)

    myalipay = init_alipay_cfg()
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
        qrcode_url = get_qr_code(code_url, subject, out_trade_no)
        qrcode_file_name = os.path.basename(qrcode_url)
        # return code_url
    return render_template('alipay/show_qr.html', out_trade_no = out_trade_no, subject = subject, amount = amount, qrcode_file_name=qrcode_file_name)


def get_qr_code(code_url, subject, out_trade_no):
    '''
    生成二维码
    :return None
    '''
    # print(code_url)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=1
    )
    qr.add_data(code_url)  # 二维码所含信息
    img = qr.make_image()  # 生成二维码图片
    filename = str(subject) + str(out_trade_no) + str(".png")
    outputfile = os.path.join(os.getcwd(), 'app/static/img/alipay_qr/', filename)
    img.save(outputfile)
    print('二维码保存成功！')
    return outputfile

#@bp.route('/show_qr/<product>/<int:amount>', methods=['GET','POST'])
def preCreateOrder(product, out_trade_no, total_amount):
    '''
    创建预付订单
    :return None：表示预付订单创建失败  [或]  code_url：二维码url
    '''
    out_trade_no_time = int(time.time())
    out_trade_no = str(product) + out_trade_no_time
    subject = product
    result = init_alipay_cfg().api_alipay_trade_precreate(
        subject=product,
        out_trade_no=out_trade_no,
        total_amount=total_amount)
    print('返回值：', result)
    code_url = result.get('qr_code')
    if not code_url:
        print(result.get('预付订单创建失败：', 'msg'))
        return
    else:
        get_qr_code(code_url, subject, out_trade_no)
        # return code_url


@bp.route('/query_order1/', methods=['GET','POST'])
def query_order1(cancel_time = 10):
    '''
    :param out_trade_no: 商户订单号
    :return: None
    '''
    cancel_time = int(current_app.config['CANCEL_TIME'])
    out_trade_no = request.form['out_trade_no']
    print('预付订单已创建,请在%s秒内扫码支付,过期订单将被取消！' % cancel_time)
    # check order status
    _time = 0
    looptime = int(cancel_time/2)
    for i in range(looptime):
        print("now sleep 2s")
        time.sleep(2)
        result = init_alipay_cfg().api_alipay_trade_query(out_trade_no=out_trade_no)
        if result.get("trade_status", "") == "TRADE_SUCCESS":
            print('订单已支付!')
            print('订单查询返回值：', result)
            return 'paied'
        _time += 2
        if _time >= cancel_time:
            a=cancel_order(out_trade_no)
            print(a)
            return "canceled"


@bp.route('/query_order/', methods=['GET','POST'])
@bp.route('/query_order/<out_trade_no>', methods=['GET','POST'])
def query_order(out_trade_no, cancel_time = 10):
    '''
    :param out_trade_no: 商户订单号
    :return: None
    '''
    out_trade_no = request.form['out_trade_no']
    print('预付订单已创建,请在%s秒内扫码支付,过期订单将被取消！' % cancel_time)
    # check order status
    _time = 0
    looptime = int(cancel_time/2)
    for i in range(looptime):
        print("now sleep 2s")
        time.sleep(2)

        result = init_alipay_cfg().api_alipay_trade_query(out_trade_no=out_trade_no)
        if result.get("trade_status", "") == "TRADE_SUCCESS":
            print('订单已支付!')
            print('订单查询返回值：', result)
            return "paied"

        _time += 2
        if _time >= cancel_time:
            a = cancel_order(out_trade_no)
            if a == 1:
                print("order canceled successfully")
            elif a == 2:
                print("order canceled failed")
            return "canceled"


def cancel_order(out_trade_no):
    '''
    撤销订单
    :param out_trade_no:
    :param cancel_time: 撤销前的等待时间(若未支付)，撤销后在商家中心-交易下的交易状态显示为"关闭"
    :return:
    '''
    result = init_alipay_cfg().api_alipay_trade_cancel(out_trade_no=out_trade_no)
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
    '''
    退款操作
    :param out_trade_no: 商户订单号
    :param refund_amount: 退款金额，小于等于订单金额
    :param out_request_no: 商户自定义参数，用来标识该次退款请求的唯一性,可使用 out_trade_no_退款金额*100 的构造方式
    :return:
    '''
    result = init_alipay_cfg().api_alipay_trade_refund(out_trade_no=out_trade_no,
                                                       refund_amount=refund_amount,
                                                       out_request_no=out_request_no)

    if result["code"] == "10000":
        return result  # 接口调用成功则返回result
    else:
        return result["msg"]  # 接口调用失败则返回原因


def refund_query(out_request_no, out_trade_no):
    '''
    退款查询：同一笔交易可能有多次退款操作（每次退一部分）
    :param out_request_no: 商户自定义的单次退款请求标识符
    :param out_trade_no: 商户订单号
    :return:
    '''
    result = init_alipay_cfg().api_alipay_trade_fastpay_refund_query(out_request_no, out_trade_no=out_trade_no)

    if result["code"] == "10000":
        return result  # 接口调用成功则返回result
    else:
        return result["msg"]  # 接口调用失败则返回原因

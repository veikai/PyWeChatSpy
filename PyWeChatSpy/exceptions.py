class SpyError(Exception):
    def __init__(self, err):
        super(Exception, self).__init__(err)


class GetWeChatVersionError(SpyError):
    def __init__(self):
        super(Exception, self).__init__("Get WeChat Version Failed,Please Check Registry")


class WrongWeChatVersionError(SpyError):
    def __init__(self):
        super(Exception, self).__init__(f"Unsuitable WeChat Version")


class GetWeChatPathError(SpyError):
    def __init__(self):
        super(Exception, self).__init__("Get WeChat Install Path Failed,,Please Check Registry")


class CreateProcessError(SpyError):
    def __init__(self, multi=True):
        if multi:
            super(Exception, self).__init__("Create Multi WeChat Process Failed")
        else:
            super(Exception, self).__init__("Create WeChat Process Failed")


class GetLoginWndHandleError(SpyError):
    def __init__(self):
        super(Exception, self).__init__("Get WeChat Login Window Handle Failed")


class InjectError(SpyError):
    def __init__(self, err):
        super(Exception, self).__init__(err)


def handle_error_code(error_code):
    error_code = str(error_code)
    if error_code == "-1":
        raise GetWeChatVersionError()
    elif error_code == "-2":
        raise WrongWeChatVersionError()
    elif error_code == "-3":
        raise GetWeChatPathError()
    elif error_code == "-4":
        raise CreateProcessError()
    elif error_code == "-5":
        raise CreateProcessError(False)
    elif error_code == "-6":
        raise GetLoginWndHandleError()
    elif error_code == "-7":
        raise InjectError("Apply For Virtual Memory Failed")
    elif error_code == "-8":
        raise InjectError("Write DLL Path Into Memory Failed")
    elif error_code == "-9":
        raise InjectError("Get Function LoadLibraryA Address Failed")
    elif error_code == "-10":
        raise InjectError("Create Remote Thread Failed")


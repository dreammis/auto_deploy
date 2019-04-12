//页面自适应；不同的屏幕获取不同的初始宽度以rem模式获取宽度，原始比例1rem=100px；
export function adtion(sw) {
    const w = document.documentElement.clientWidth;
    let f = w / sw * 100;
    f = f > 100 ? 100 + "px" : f + "px";
    document.documentElement.style.fontSize = f;
}


//不同的屏幕大小显示不同的meum；
export const pcOrMobile = (callback) => {
    let w = document.documentElement.clientWidth;
    let pf = w > 768 ? true : false;
    window.onresize = function () {
        w = document.documentElement.clientWidth;
        pf = w > 768 ? true : false;
        callback(pf);
        adtion(1024);
    };
    callback(pf);
};

//判断图片是否更新；更新则加载新图片
export const errorImgHandling = (nextProsInfo, prePropsInfo, preProps, defaultAvatar) => {
    if (nextProsInfo != prePropsInfo) {
        preProps.setState({
            imgSrc: nextProsInfo ? nextProsInfo : defaultAvatar
        });
    }
};


//图片加载失败时获取默认图片
export const imgError = (obj, defaultAvatar) => {
    obj.setState({
        imgSrc: defaultAvatar
    });
    return false;
};


//获取url参数
export const GetQueryString = (name) => {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
    var r = window.location.search.substr(1).match(reg);
    if (r != null) {
        return unescape(r[2]);
    } return null;
};

//获取传递参数

export const getPropsStirng = (props, name) => {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
    var r = props.match(reg);
    if (r != null) {
        return unescape(r[2]);
    } return null;
};

export const loadScript = (src, type) => {
    const script = document.createElement("script");
    script.type = type;
    script.src = src;
    const head = document.head || document.getElementsByTagName("head")[0];
    head.appendChild(script);
};

export const addMeta = (name, itemprop, content) => {
    const head = document.head || document.getElementsByTagName("head")[0];
    const meta = document.createElement("meta");
    meta.name = name;
    meta.itemprop = itemprop;
    meta.content = content;
    head.appendChild(meta);
};


export const isWeiXin = () => {
    var ua = window.navigator.userAgent.toLowerCase();
    if (ua.match(/MicroMessenger/i) == "micromessenger") {
        return true;
    } else {
        return false;
    }
};

export const isAlipay = () => {
    var ua = window.navigator.userAgent.toLowerCase();
    if (ua.match(/AlipayClient/i) == "alipayClient") {
        return true;
    } else {
        return false;
    }
}

export const checkFrom = () => {
    let ua = navigator.userAgent,
        isWindowsPhone = /(?:Windows Phone)/.test(ua),
        isSymbian = /(?:SymbianOS)/.test(ua) || isWindowsPhone,
        isAndroid = /(?:Android)/.test(ua),
        isFireFox = /(?:Firefox)/.test(ua),
        isChrome = /(?:Chrome|CriOS)/.test(ua),
        isTablet = /(?:iPad|PlayBook)/.test(ua) || (isAndroid && !/(?:Mobile)/.test(ua)) || (isFireFox && /(?:Tablet)/.test(ua)),
        isPhone = /(?:iPhone)/.test(ua) && !isTablet,
        isPc = !isPhone && !isAndroid && !isSymbian;
    return {
        isTablet: isTablet,
        isPhone: isPhone,
        isAndroid: isAndroid,
        isPc: isPc
    };
};

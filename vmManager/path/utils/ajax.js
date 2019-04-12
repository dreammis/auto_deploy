import {message} from 'antd';
const ajaxSub = (url, type, data) => {
    return new Promise(function (resolve, reject) {
        $.ajax({
            url: url,
            type: type,
            data: data,
            success: function (data) {
                if (data.status == 0 || !data.status) {
                    resolve(data);
                }else {
                    message.error(data.message);
                }
            },
            error: function () {
                reject(data);
            }
        });
    }).catch(function (reason) {
        console.log('Failed: ' + reason);
    });
}

export default ajaxSub;
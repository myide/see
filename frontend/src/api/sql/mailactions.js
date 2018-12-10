import axios from '../../libs/http';

const mailactions = '/api/sqlmng/mailactions/';

export function GetMailActions(params) {
    return axios({
        url: mailactions,
        method: 'get',
        params
    });
}

export function SetMailActions(data) {
    return axios({
        url: mailactions,
        method: 'post',
        data: data
    });
}
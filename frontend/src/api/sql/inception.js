import axios from '../../libs/http';

const inceptions = '/api/sqlmng/inceptions/';

export function GetSqlList (params) {
    return axios({
        url: inceptions,
        method: 'get',
        params
    });
}

export function GetSqlDetail (id) {
    return axios.get(inceptions + id + '/');
}

export function SqlAction (id, action) {
    return axios.get(inceptions + id + '/' + action + '/');
}

export function SetCron (id, action, data) {
    return axios({
        url: inceptions + id + '/' + action + '/',
        method: 'post',
        data: data
    });
}
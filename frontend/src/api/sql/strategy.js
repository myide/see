import axios from '../../libs/http';

const strategy = '/api/sqlmng/strategy/';

export function GetStrategyList(params) {
    return axios({
        url: strategy,
        method: 'get',
        params
    });
}

export function UpdateStrategy(id, data) {
    return axios({
        url: strategy + id + '/',
        method: 'put',
        data: data
    });
}

export function CreateStrategy(data) {
    return axios({
        url: strategy,
        method: 'post',
        data: data
    });
}
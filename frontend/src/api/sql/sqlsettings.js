import axios from '../../libs/http';

const sqlsettings = '/api/sqlmng/sqlsettings/';

export function GetFWList(params) {
    return axios({
        url: sqlsettings,
        method: 'get',
        params
    });
}

export function UpdateFW(id, data) {
    return axios({
        url: sqlsettings + id + '/',
        method: 'put',
        data: data
    });
}

export function CreateFW(data) {
    return axios({
        url: sqlsettings,
        method: 'post',
        data: data
    });
}
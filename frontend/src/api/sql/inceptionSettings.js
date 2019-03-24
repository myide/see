import axios from '../../libs/http';

const variablesUrl = '/api/sqlmng/inception/variables/';
const connectionUrl = '/api/sqlmng/inception/connection/';
const backupUrl = '/api/sqlmng/inception/backup/';
const checkConnUrl = '/api/sqlmng/inception/conncheck/';

export function GetInceptionVariables (params) {
    return axios({
        url: variablesUrl,
        method: 'get',
        params
    });
}

export function SetInceptionVariables (data) {
    return axios({
        url: variablesUrl,
        method: 'post',
        data: data
    });
}

export function CheckConn (data) {
    return axios({
        url: checkConnUrl,
        method: 'post',
        data: data
    });
}

export function GetInceptionBackup (params) {
    return axios({
        url: backupUrl,
        method: 'get',
        params
    })
}

export function GetInceptionConnection (params) {
    return axios({
        url: connectionUrl,
        method: 'get',
        params
    });
}

export function UpdateInceptionConnection (id, data) {
    return axios({
        url: connectionUrl + id + '/',
        method: 'put',
        data: data
    });
}

export function CreateInceptionConnection (data) {
    return axios({
        url: connectionUrl,
        method: 'post',
        data: data
    });
}

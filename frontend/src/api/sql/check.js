import axios from '../../libs/http'

const autoSelects = '/api/sqlmng/autoselects/'
const inceptionCheck = '/api/sqlmng/inceptioncheck/'
const personalSettings = '/api/sqlmng/personalsettings/'

export function GetSelectData(data) {
    return axios({
        url: autoSelects,
        method: 'post',
        data: data
    })
}

export function CheckSql(data) {
    return axios({
        url: inceptionCheck,
        method: 'post',
        data: data
    })
}

export function GetPersonalSettings(params) {
    return axios({
        url: personalSettings,
        method: 'get',
        params
    })
}

export function CreatePersonalSettings(data) {
    return axios({
        url: personalSettings,
        method: 'post',
        data: data
    })
}


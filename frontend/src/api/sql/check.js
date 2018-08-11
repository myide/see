import axios from '../../libs/http'

const autoSelects = '/api/sqlmng/autoselects/'
const inceptionCheck = '/api/sqlmng/inceptioncheck/'

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


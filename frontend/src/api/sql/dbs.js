import axios from '../../libs/http'

const dbConfs = '/api/sqlmng/dbconfs/'

export function GetDbList(params) {
    return axios({
      url: dbConfs,
      method: 'get',
      params
    })
}

export function UpdateDb(id, data) {
    return axios({
        url: dbConfs + id + '/',
        method: 'put',
        data: data
    })
}

export function CreateDb(data) {
    return axios({
        url: dbConfs,
        method: 'post',
        data: data
    })
}

export function DeleteDb(id) {
    return axios({
        url: dbConfs + id + '/',
        method: 'delete',
    })
}

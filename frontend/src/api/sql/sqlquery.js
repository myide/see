import axios from '../../libs/http'
const dbConfs = '/api/sqlmng/dbconfs/'

export function GetTableList(id) {
    return axios.get(dbConfs + id + '/tables/')
}

export function GetTableInfo(id, table_name) {
    return axios.get(dbConfs + id + '/table_info/?table_name=' + table_name)
}

export function GetSqlAdvisor(id, sql) {
    return axios.get(dbConfs + id + '/sql_advisor/?sql=' + sql)
}


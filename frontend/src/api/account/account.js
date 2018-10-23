import axios from '../../libs/http';

const users = '/api/account/users/';
const groups = '/api/account/groups/';
const permissions = '/api/account/permissions/';
const personal = '/api/account/personal/'

export function GetUserList(params) {
    return axios({
        url: users,
        method: 'get',
        params
    });
}

export function UpdateUser(id, data) {
    return axios({
        url: users + id + '/',
        method: 'put',
        data: data
    });
}

export function CreateUser(data) {
    return axios({
        url: users,
        method: 'post',
        data: data
    });
}

export function DeleteUser(id) {
    return axios({
        url: users + id + '/',
        method: 'delete',
    });
}

export function GetGroupList(params) {
    return axios({
        url: groups,
        method: 'get',
        params
    });
}

export function CreateGroup(data) {
    return axios({
        url: groups,
        method: 'post',
        data: data
    });
}

export function UpdateGroup(id, data) {
    return axios({
        url: groups + id + '/',
        method: 'put',
        data: data
    });
}

export function DeleteGroup(id) {
    return axios({
        url: groups + id + '/',
        method: 'delete',
    });
}

export function GetPermissonList(params) {
    return axios({
        url: permissions,
        method: 'get',
        params
    });
}

export function GetPersonal(params) {
    return axios({
        url: personal,
        method: 'get',
        params
    });
}

export function UpdatePersonal(data) {
    return axios({
        url: personal,
        method: 'post',
        data: data
    });
}
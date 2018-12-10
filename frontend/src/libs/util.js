import axios from 'axios'
import env from '../../build/env'
import semver from 'semver'
import packjson from '../../package.json'

let util = {}

util.highlight = 'alter|and|as|asc|between|count|create|delete|desc|distinct|drop|from|having|in|insert|into|is|join|like|not|on|or|order|select|set|table|union|update|values|where|accessible|action|add|after|algorithm|all|analyze|asensitive|at|authors|auto_increment|autocommit|avg|avg_row_length|before|binary|binlog|both|btree|cache|call|cascade|cascaded|case|catalog_name|chain|change|changed|character|check|checkpoint|checksum|class_origin|client_statistics|close|coalesce|code|collate|collation|collations|column|columns|comment|commit|committed|completion|concurrent|condition|connection|consistent|constraint|contains|continue|contributors|convert|cross|current_date|current_time|current_timestamp|current_user|cursor|data|database|databases|day_hour|day_microsecond|day_minute|day_second|deallocate|dec|declare|default|delay_key_write|delayed|delimiter|des_key_file|describe|deterministic|dev_pop|dev_samp|deviance|directory|disable|discard|distinctrow|div|dual|dumpfile|each|elseif|enable|enclosed|end|ends|engine|engines|enum|errors|escape|escaped|even|event|events|every|execute|exists|exit|explain|extended|fast|fetch|field|fields|first|flush|for|force|foreign|found_rows|full|fulltext|function|general|global|grant|grants|group|groupby_concat|handler|hash|help|high_priority|hosts|hour_microsecond|hour_minute|hour_second|if|ignore|ignore_server_ids|import|index|index_statistics|infile|inner|innodb|inout|insensitive|insert_method|install|interval|invoker|isolation|iterate|key|keys|kill|language|last|leading|leave|left|level|limit|linear|lines|list|load|local|localtime|localtimestamp|lock|logs|low_priority|master|master_heartbeat_period|master_ssl_verify_server_cert|masters|match|max|max_rows|maxvalue|message_text|middleint|migrate|min|min_rows|minute_microsecond|minute_second|mod|mode|modifies|modify|mutex|mysql_errno|natural|next|no|no_write_to_binlog|offline|offset|one|online|open|optimize|option|optionally|out|outer|outfile|pack_keys|parser|partition|partitions|password|phase|plugin|plugins|prepare|preserve|prev|primary|privileges|procedure|processlist|profile|profiles|purge|query|quick|range|read|read_write|reads|real|rebuild|recover|references|regexp|relaylog|release|remove|rename|reorganize|repair|repeatable|replace|acequire|resignal|restrict|resume|return|returns|revoke|right|rlike|rollback|rollup|row|row_format|rtree|savepoint|schedule|schema|schema_name|schemas|second_microsecond|security|sensitive|separator|serializable|server|session|share|show|signal|slave|slow|smallint|snapshot|soname|spatial|specific|sql|sql_big_result|sql_buffer_result|sql_cache|sql_calc_found_rows|sql_no_cache|sql_small_result|sqlexception|sqlstate|sqlwarning|ssl|start|starting|starts|status|std|stddev|stddev_pop|stddev_samp|storage|straight_join|subclass_origin|sum|suspend|table_name|table_statistics|tables|tablespace|temporary|terminated|to|trailing|transaction|trigger|triggers|truncate|uncommitted|undo|uninstall|unique|unlock|upgrade|usage|use|use_frm|user|user_resources|user_statistics|using|utc_date|utc_time|utc_timestamp|value|variables|varying|view|views|warnings|when|while|with|work|write|xa|xor|year_month|zerofill|begin|do|then|else|loop|repeat|by|bool|boolean|bit|blob|decimal|double|enum|float|long|longblob|longtext|medium|mediumblob|mediumint|mediumtext|time|timestamp|tinyblob|tinyint|tinytext|text|bigint|int|int1|int2|int3|int4|int8|integer|float|float4|float8|double|char|varbinary|varchar|varcharacter|precision|date|datetime|year|unsigned|signed|numeric|ucase|lcase|mid|len|round|rank|now|format|coalesce|ifnull|isnull|nvl'

util.title = function(title) {
    title = title || 'see'
    window.document.title = title
}

const tokenUrl = 'http://sqlweb:200/api-token-auth/'

const ajaxUrl = env === 'development' ?
    'http://sqlweb:200' :
    env === 'production' ?
    'https://www.url.com' :
    'https://debug.url.com'

util.ajax = axios.create({
    tokenURL: tokenUrl,
    baseURL: ajaxUrl,
    timeout: 30000
})

util.inOf = function(arr, targetArr) {
    let res = true
    arr.forEach(item => {
        if (targetArr.indexOf(item) < 0) {
            res = false
        }
    })
    return res
}

util.oneOf = function(ele, targetArr) {
    if (targetArr.indexOf(ele) >= 0) {
        return true
    } else {
        return false
    }
}

util.showThisRoute = function(itAccess, currentAccess) {
    if (typeof itAccess === 'object' && Array.isArray(itAccess)) {
        return util.oneOf(currentAccess, itAccess)
    } else {
        return itAccess === currentAccess
    }
}

util.getRouterObjByName = function(routers, name) {
    if (!name || !routers || !routers.length) {
        return null
    }
    // debugger
    let routerObj = null
    for (let item of routers) {
        if (item.name === name) {
            return item
        }
        routerObj = util.getRouterObjByName(item.children, name)
        if (routerObj) {
            return routerObj
        }
    }
    return null
}

util.handleTitle = function(vm, item) {
    if (typeof item.title === 'object') {
        return vm.$t(item.title.i18n)
    } else {
        return item.title
    }
}

util.setCurrentPath = function(vm, name) {
    let title = ''
    let isOtherRouter = false
    vm.$store.state.app.routers.forEach(item => {
        if (item.children.length === 1) {
            if (item.children[0].name === name) {
                title = util.handleTitle(vm, item)
                if (item.name === 'otherRouter') {
                    isOtherRouter = true
                }
            }
        } else {
            item.children.forEach(child => {
                if (child.name === name) {
                    title = util.handleTitle(vm, child)
                    if (item.name === 'otherRouter') {
                        isOtherRouter = true
                    }
                }
            })
        }
    })
    let currentPathArr = []
    if (name === 'home_index') {
        currentPathArr = [{
            title: util.handleTitle(vm, util.getRouterObjByName(vm.$store.state.app.routers, 'home_index')),
            path: '',
            name: 'home_index'
        }]
    } else if ((name.indexOf('_index') >= 0 || isOtherRouter) && name !== 'home_index') {
        currentPathArr = [{
                title: util.handleTitle(vm, util.getRouterObjByName(vm.$store.state.app.routers, 'home_index')),
                path: '/home',
                name: 'home_index'
            },
            {
                title: title,
                path: '',
                name: name
            }
        ]
    } else {
        let currentPathObj = vm.$store.state.app.routers.filter(item => {
            if (item.children.length <= 1) {
                return item.children[0].name === name
            } else {
                let i = 0
                let childArr = item.children
                let len = childArr.length
                while (i < len) {
                    if (childArr[i].name === name) {
                        return true
                    }
                    i++
                }
                return false
            }
        })[0]
        if (currentPathObj.children.length <= 1 && currentPathObj.name === 'home') {
            currentPathArr = [{
                title: '首页',
                path: '',
                name: 'home_index'
            }]
        } else if (currentPathObj.children.length <= 1 && currentPathObj.name !== 'home') {
            currentPathArr = [{
                    title: '首页',
                    path: '/home',
                    name: 'home_index'
                },
                {
                    title: currentPathObj.title,
                    path: '',
                    name: name
                }
            ]
        } else {
            let childObj = currentPathObj.children.filter((child) => {
                return child.name === name
            })[0]
            currentPathArr = [{
                    title: '首页',
                    path: '/home',
                    name: 'home_index'
                },
                {
                    title: currentPathObj.title,
                    path: '',
                    name: currentPathObj.name
                },
                {
                    title: childObj.title,
                    path: currentPathObj.path + '/' + childObj.path,
                    name: name
                }
            ]
        }
    }
    vm.$store.commit('setCurrentPath', currentPathArr)

    return currentPathArr
}

util.openNewPage = function(vm, name, argu, query) {
    let pageOpenedList = vm.$store.state.app.pageOpenedList
    let openedPageLen = pageOpenedList.length
    let i = 0
    let tagHasOpened = false
    while (i < openedPageLen) {
        if (name === pageOpenedList[i].name) { // 页面已经打开
            vm.$store.commit('pageOpenedList', {
                index: i,
                argu: argu,
                query: query
            })
            tagHasOpened = true
            break
        }
        i++
    }
    if (!tagHasOpened) {
        let tag = vm.$store.state.app.tagsList.filter((item) => {
            if (item.children) {
                return name === item.children[0].name
            } else {
                return name === item.name
            }
        })
        tag = tag[0]
        if (tag) {
            tag = tag.children ? tag.children[0] : tag
            if (argu) {
                tag.argu = argu
            }
            if (query) {
                tag.query = query
            }
            vm.$store.commit('increateTag', tag)
        }
    }
    vm.$store.commit('setCurrentPageName', name)
}

util.toDefaultPage = function(routers, name, route, next) {
    let len = routers.length
    let i = 0
    let notHandle = true
    while (i < len) {
        if (routers[i].name === name && routers[i].children && routers[i].redirect === undefined) {
            route.replace({
                name: routers[i].children[0].name
            })
            notHandle = false
            next()
            break
        }
        i++
    }
    if (notHandle) {
        next()
    }
}

util.fullscreenEvent = function(vm) {
    vm.$store.commit('initCachepage')
        // 权限菜单过滤相关
    vm.$store.commit('updateMenulist')
        // 全屏相关
}

util.checkUpdate = function(vm) {
    axios.get('https://api.github.com/repos/iview/iview-admin/releases/latest').then(res => {
        let version = res.data.tag_name
        vm.$Notice.config({
            duration: 0
        })
        if (semver.lt(packjson.version, version)) {
            vm.$Notice.info({
                title: 'iview-admin更新啦',
                desc: '<p>iView-admin更新到了' + version + '了，去看看有哪些变化吧</p><a style="font-size:13px;" href="https://github.com/iview/iview-admin/releases" target="_blank">前往github查看</a>'
            })
        }
    })
}

export default util
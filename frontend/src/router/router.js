import Main from '@/views/Main.vue';

// 不作为Main组件的子页面展示的页面单独写，如下
export const loginRouter = {
    path: '/login',
    name: 'login',
    meta: {
        title: 'Login - 登录'
    },
    component: () =>
        import ('@/views/login.vue')
};

// 作为Main组件的子页面展示但是不在左侧菜单显示的路由写在otherRouter里
export const otherRouter = {
    path: '/',
    name: 'otherRouter',
    redirect: '/home',
    component: Main,
    children: [{
            path: 'home',
            title: { i18n: 'home' },
            name: 'home_index',
            component: () =>
                import ('@/views/home/home.vue')
        },
        {
            path: 'ownspace',
            title: '个人中心',
            name: 'ownspace_index',
            component: () =>
                import ('@/views/own-space/own-space.vue')
        },
        {
            path: 'inceptionsql/:id',
            title: 'sql详情',
            name: 'inceptiondetail',
            component: () =>
                import ('@/views/sql/inceptiondetail.vue'),
        }, // 用户展示图书详情

    ]
};

// 作为Main组件的子页面展示并且在左侧菜单显示的路由写在appRouter里
export const appRouter = [{
        path: '/access-test',
        icon: 'lock-combination',
        title: '权限测试页',
        name: 'accesstest',
        access: 0,
        component: Main,
        children: [{
            path: 'index',
            title: '权限测试页',
            name: 'accesstest_index',
            access: 0,
            component: () =>
                import ('@/views/access/access-test.vue')
        }]
    },

    {
        path: '/pandect',
        icon: 'social-tumblr',
        title: '总览',
        name: 'Test',
        component: Main,
        children: [{
                path: 'aa',
                title: '测试页aa',
                name: 'aa',
                component: () =>
                    import ('@/views/test/aa.vue')
            },
            {
                path: 'bb',
                title: '测试页bb',
                name: 'bb',
                component: () =>
                    import ('@/views/test/bb.vue')
            },
        ]
    },

    {
        path: '/sqlmng',
        icon: 'shuffle',
        title: 'SQL上线',
        name: 'sq',
        component: Main,
        children: [{
                path: 'check',
                title: 'sql审核',
                name: 'check',
                component: () =>
                    import ('@/views/sql/check.vue')
            },
            {
                path: 'inceptionlist',
                title: 'sql处理',
                name: 'inceptionlist',
                component: () =>
                    import ('@/views/sql/inceptionlist.vue')
            },
            {
                path: 'dblist',
                title: '目标数据库',
                name: 'dblist',
                component: () =>
                    import ('@/views/sql/dblist.vue')
            },
        ]
    },


    {
        path: '/accountmng',
        icon: 'person',
        title: '用户管理',
        name: 'am',
        component: Main,
        children: [{
                path: 'user',
                title: '用户',
                name: 'user',
                component: () =>
                    import ('@/views/account/user.vue')
            },
            {
                path: 'group',
                title: '组',
                name: 'group',
                component: () =>
                    import ('@/views/account/group.vue')
            },

        ]
    },



];

// 所有上面定义的路由都要写在下面的routers里
export const routers = [
    loginRouter,
    otherRouter,
    ...appRouter,
];
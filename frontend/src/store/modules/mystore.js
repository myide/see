import Cookies from 'js-cookie';

const mystore = {
    state: {
        count: 6
    },

    mutations: {
        add(state) {
            state.count += 1;
        },
        reduce(state, payload) {
            state.count -= payload.num;
        },
    },
    getters: {
        gcount: function(state) {
            state.count += 200;
            return state.count;
        }
    },

    actions: {
        addAsync({ commit }) {
            setTimeout(() => {
                commit('add');
            }, 1000);
        }
    }
}

export default mystore
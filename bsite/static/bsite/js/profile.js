class MiTabs {
    constructor(menu, body, settings = {}) {
        this.menu = document.querySelector(menu);
        this.body = document.querySelector(body);
        this.settings = {
            contentCallback: settings.contentCallback ? settings.contentCallback : () => { return 'The tab does not exist'},
            changeTabCallback: settings.changeTabCallback ? settings.changeTabCallback : false,
        }
        this.menu.addEventListener('click', this.#changeTab.bind(this));
    }

    async #changeTab(event) {

        let target = event.target.closest('.MiTab-narrow');

        if(!target || target.dataset.loading) return false;

        const tabPageId = target.getAttribute('data-tab');

        if(!this.body.querySelector(`[data-tabBody="${tabPageId}"]`)) {
            target.dataset.loading = true;
            await this.#createTab(tabPageId);
            target.removeAttribute('data-loading');
        }

        let block = this.body.querySelector(`[data-tabBody="${tabPageId}"]`);
        if(block.classList.contains('active')) return false;


        let activeNarrow = this.menu.querySelector(`.MiTab-narrow.active-tabLink`)

        if(activeNarrow) activeNarrow.classList.remove('active-tabLink');

        let activeBody = this.body.querySelector(`.MiTab-item.active`);

        if(activeBody) activeBody.classList.remove('active');


        block.classList.add('active');
        target.classList.add('active-tabLink');

        if(this.settings.changeTabCallback) this.settings.changeTabCallback({tabPageId: tabPageId, block: block, prevBlock: activeBody});

    }

    async #createTab(tabPageId) {
        let newTabPage = document.createElement('div');

        newTabPage.classList.add('MiTab-item');
        newTabPage.classList.add('MiTab-item');
        newTabPage.dataset.tabbody = tabPageId;

        let content = await this.settings.contentCallback(tabPageId);

        if(Array.isArray(content)) {
            content.forEach( item => {

                newTabPage.append(item);

            })
        } else {
            newTabPage.append(content);
        }

        this.body.append(newTabPage);

        return true;
    }

}


const installTabs = () => {
    const tabs = document.querySelectorAll('[data-tab-container]');
    if(tabs.length) {
        tabs.forEach( tab => {
            const tab_id = tab.dataset.tabContainer;
            new MiTabs(`[data-tab-menu="${tab_id}"]`, `[data-tab-container="${tab_id}"]`);
        })
    }
}

addOnLoadEvent(installTabs)

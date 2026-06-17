class OctopusGreenerNightsMemoryCard extends HTMLElement {
    constructor() {
        super();
        this._lastRendered = null;
        this._refreshTimer = null;
    }

    setConfig(config) {
        this.config = {
            entity: "sensor.octopus_greener_nights_memory",
            ...config
        };

        if (!this.config.entity) {
            throw new Error("Entity required");
        }
    }

    set hass(hass) {
        this._hass = hass;
        this.update();
    }

    connectedCallback() {
        if (this._refreshTimer) return;

        this._refreshTimer = window.setInterval(
            () => this.refreshEntity(),
            30 * 60 * 1000
        );
    }

    disconnectedCallback() {
        if (!this._refreshTimer) return;

        window.clearInterval(this._refreshTimer);
        this._refreshTimer = null;
    }

    refreshEntity() {
        if (!this._hass || !this.config?.entity) return;

        this._hass.callService("homeassistant", "update_entity", {
            entity_id: this.config.entity
        });
    }

    colour(v) {
        const c = this.config || {};

        const green = c.color_green || "var(--success-color)";
        const orange = c.color_orange || "var(--warning-color)";
        const red = c.color_red || "var(--error-color)";

        return v === "green" ? green : v === "orange" ? orange : red;
    }

    textColour(v) {
        const c = this.config || {};

        const green = c.text_color_green || "#ffffff";
        const orange = c.text_color_orange || "#ffffff";
        const red = c.text_color_red || "#ffffff";

        return v === "green" ? green : v === "orange" ? orange : red;
    }

    shouldRender(next) {
        if (!this._lastRendered) return true;
        return this._lastRendered !== next;
    }

    update() {
        if (!this._hass || !this.config) return;

        const entity = this._hass.states[this.config.entity];
        const memory = entity?.attributes?.memory || {};

        const key = JSON.stringify({ memory, config: this.config });

        if (!this.shouldRender(key)) return;
        this._lastRendered = key;

        this.render(memory);
    }

    render(memory) {
        const today = new Date();

        const tileHeight = this.config.tile_height || 56;
        const todayFont = this.config.today_font_size || 14;
        const dateFont = this.config.date_font_size || todayFont;

        const days = Array.from({ length: 7 }).map((_, i) => {
            const d = new Date(today);
            d.setDate(today.getDate() + i);
            const iso = d.toISOString().split("T")[0];
            return { d, state: memory[iso] || "red" };
        });

        const titleMode = this.config.title_mode || "large";
        const showTitle = this.config.title_mode !== "none" && this.config.title;

        const titleHtml = showTitle
        ? titleMode === "compact"
        ? `<div style="padding:10px 16px 2px 16px;font-size:16px;font-weight:500;opacity:0.9;">
        ${this.config.title}
        </div>`
        : `<div style="padding:14px 16px 4px 16px;font-size:20px;font-weight:500;">
        ${this.config.title}
        </div>`
        : "";

        const cardInnerPadding =
        titleMode === "compact" ? "4px 12px 12px 12px" : "8px 12px 12px 12px";

        const cellBase = `
        height:${tileHeight}px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        text-align:center;
        border-radius:12px;
        line-height:1.2;
        `;

        if (!this._root) {
            this._root = document.createElement("ha-card");
            this.appendChild(this._root);
        }

        this._root.innerHTML = `
        ${titleHtml}
        <div style="padding:${cardInnerPadding};">

        <div style="
        background:${this.colour(days[0].state)};
        color:${this.textColour(days[0].state)};
        ${cellBase}
        font-weight:700;
        font-size:${todayFont}px;
        margin-bottom:8px;">
        TODAY
        </div>

        <div style="
        display:grid;
        grid-template-columns:repeat(3, minmax(0, 1fr));
        gap:8px;
        ">
        ${days.slice(1).map(d => `
            <div style="
            background:${this.colour(d.state)};
            color:${this.textColour(d.state)};
            ${cellBase}
            font-size:${dateFont}px;
            ">
            <div>${d.d.toLocaleDateString("en-GB",{weekday:"short"})}</div>
            <div>${d.d.getDate()}</div>
            </div>
            `).join("")}
            </div>

            </div>
            `;
    }

    static getStubConfig() {
        return {
            entity: "sensor.octopus_greener_nights_memory",
            title: "Octopus Greener Nights",
            title_mode: "large",
            tile_height: 56,
            today_font_size: 14,
            date_font_size: 14,
            color_green: "#5d9e52",
            color_orange: "#f2aa3c",
            color_red: "#ca5040",
            text_color_green: "#ffffff",
            text_color_orange: "#ffffff",
            text_color_red: "#ffffff"
        };
    }

    static getConfigForm() {
        return {
            schema: [
                { name: "title", selector: { text: {} } },

                {
                    name: "title_mode",
                    selector: {
                        select: {
                            options: [
                                { value: "large", label: "Large" },
                                { value: "compact", label: "Compact" },
                                { value: "none", label: "No title" }
                            ]
                        }
                    }
                },

                {
                    name: "entity",
                    required: true,
                    selector: { entity: { domain: "sensor" } }
                },

                {
                    name: "tile_height",
                    selector: {
                        number: { min: 24, max: 120, step: 4, mode: "box" }
                    }
                },

                {
                    name: "today_font_size",
                    selector: {
                        number: { min: 10, max: 40, step: 1, mode: "box" }
                    }
                },

                {
                    name: "date_font_size",
                    selector: {
                        number: { min: 10, max: 40, step: 1, mode: "box" }
                    }
                },

                {
                    name: "color_green",
                    label: "Colour: Greener Night",
                    selector: { text: {} }
                },
                {
                    name: "color_orange",
                    label: "Colour: Former Greener Night",
                    selector: { text: {} }
                },
                {
                    name: "color_red",
                    label: "Colour: Never a Greener Night",
                    selector: { text: {} }
                },
                {
                    name: "text_color_green",
                    label: "Text color on green tile",
                    selector: { text: {} }
                },
                {
                    name: "text_color_orange",
                    label: "Text color on orange tile",
                    selector: { text: {} }
                },
                {
                    name: "text_color_red",
                    label: "Text color on red tile",
                    selector: { text: {} }
                }
            ]
        };
    }

}

customElements.define(
    "octopus-greener-nights-memory-card",
    OctopusGreenerNightsMemoryCard
);

window.customCards = window.customCards || [];
window.customCards.push({
    type: "octopus-greener-nights-memory-card",
    name: "Octopus Greener Nights Memory Card",
    description: "7-day Greener Nights grid"
});

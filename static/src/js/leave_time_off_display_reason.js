odoo.define('logic_leaves.leave_time_off_display_reason', function (require) {
    "use strict";
    console.log('wwork')

    const CalendarRenderer = require('web.CalendarRenderer');
    const CalendarController = require('web.CalendarController');
    const CalendarModel = require('web.CalendarModel');
    const CalendarView = require('web.CalendarView');
    const viewRegistry = require('web.view_registry');

    const CustomCalendarRenderer = CalendarRenderer.extend({
        _renderEvents: function (events) {
            this._super.apply(this, arguments);
            if (this.state.showUnusualDays) {
                this._renderUnusualDays();
            }
            if (this.state.publicHolidays) {
                this._renderPublicHolidays();
            }
        },
        _renderUnusualDays: function () {
            const unusualDays = this.state.unusualDays;
            for (const [date, info] of Object.entries(unusualDays)) {
                const dayElement = this.$('.fc-day[data-date="' + date + '"]');
                if (dayElement.length) {
                    dayElement.append(`<div class="unusual-day" title="${info.reason}">${info.reason}</div>`);
                }
            }
        },
        _renderPublicHolidays: function () {
            const publicHolidays = this.state.publicHolidays;
            for (const [date, info] of Object.entries(publicHolidays)) {
                const dayElement = this.$('.fc-day[data-date="' + date + '"]');
                if (dayElement.length) {
                    dayElement.css('background-color', 'gray');
                    dayElement.append(`<div class="public-holiday">${info.name}</div>`);
                }
            }
        },
    });

    const CustomCalendarController = CalendarController.extend({
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            this.showUnusualDays = this.initialState.showUnusualDays;
            this.showPublicHolidays = this.initialState.showPublicHolidays;
        },
    });

    const CustomCalendarModel = CalendarModel.extend({
        load: function (params) {
            return this._super.apply(this, arguments).then((result) => {
                if (params.show_unusual_days) {
                    this.showUnusualDays = params.show_unusual_days;
                    return this._loadUnusualDays(params);
                }
                if (params.show_public_holidays) {
                    this.showPublicHolidays = params.show_public_holidays;
                    return this._loadPublicHolidays(params);
                }
                return result;
            });
        },
        _loadUnusualDays: function (params) {
            return this._rpc({
                model: 'hr.leave',
                method: 'get_unusual_days',
                args: [params.date_start, params.date_stop],
            }).then((unusualDays) => {
                this.unusualDays = unusualDays;
                return this;
            });
        },
        _loadPublicHolidays: function (params) {
            return this._rpc({
                model: 'public.holiday',
                method: 'search_read',
                domain: [['date', '>=', params.date_start], ['date', '<=', params.date_stop]],
                fields: ['date', 'name'],
            }).then((holidays) => {
                this.publicHolidays = {};
                for (const holiday of holidays) {
                    this.publicHolidays[holiday.date] = {
                        name: holiday.name,
                    };
                }
                return this;
            });
        },
    });

    const CustomCalendarView = CalendarView.extend({
        config: _.extend({}, CalendarView.prototype.config, {
            Model: CustomCalendarModel,
            Controller: CustomCalendarController,
            Renderer: CustomCalendarRenderer,
        }),
    });

    viewRegistry.add('custom_calendar', CustomCalendarView);
});

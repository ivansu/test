// Инициализация табов

function submitForm2(btn, e, baseParams) {
    win.actionContextJson.win_close = 1;
    win.actionContextJson.work_programs_vop2 = Ext.getCmp('{{ component.work_programs_vop.client_id }}').getValue();
    win.actionContextJson.year_graphs_vop2 = Ext.getCmp('{{ component.year_graphs_vop.client_id }}').getValue();
    win.actionContextJson.study_plans_vop2 = Ext.getCmp('{{ component.study_plans_vop.client_id }}').getValue();
    win.submitForm(btn, e, baseParams);
    win.actionContextJson.win_close = '';
    win.actionContextJson.work_programs_vop2 = '';
    win.actionContextJson.year_graphs_vop2 = '';
    win.actionContextJson.study_plans_vop2 = '';
}

function submitForm3(btn, e, baseParams) {
    win.actionContextJson.work_programs_vop2 = Ext.getCmp('{{ component.work_programs_vop.client_id }}').getValue();
    win.actionContextJson.year_graphs_vop2 = Ext.getCmp('{{ component.year_graphs_vop.client_id }}').getValue();
    win.actionContextJson.study_plans_vop2 = Ext.getCmp('{{ component.study_plans_vop.client_id }}').getValue();
    win.submitForm(btn, e, baseParams);
    win.actionContextJson.work_programs_vop2 = '';
    win.actionContextJson.year_graphs_vop2 = '';
    win.actionContextJson.study_plans_vop2 = '';
}


{% block child_code %}

{# здесь вставляется код дочерних форм в соответствующих темплейтах из плагинов #}

{% endblock %}


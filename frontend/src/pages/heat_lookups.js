        import {workspace} from '../workspace.js';
        import {el} from '../dom.js';

        const page = {
  "title": "按成品弯度反查炉温",
  "module": "预测曲线签注",
  "caption": "炉温倒查单",
  "detail": "展柜只给成品弯度：在已签注曲线的训练温区内，按片厚、工艺目标和成品弯度反查炉温。多解取离常用炉温最近者，无解则炉温留空。",
  "path": "/heat_lookups",
  "columns": [
    {
      "name": "code",
      "label": "倒查单号"
    },
    {
      "name": "profile",
      "label": "曲线版本"
    },
    {
      "name": "thick",
      "label": "片厚 mm"
    },
    {
      "name": "target",
      "label": "工艺目标弯度 mm"
    },
    {
      "name": "measured",
      "label": "成品弯度 mm"
    },
    {
      "name": "heat",
      "label": "反查炉温 °C"
    },
    {
      "name": "candidates",
      "label": "温区内候选炉温"
    },
    {
      "name": "usual_heat",
      "label": "常用炉温 °C"
    },
    {
      "name": "state",
      "label": "状态"
    },
    {
      "name": "reason",
      "label": "无解说明"
    }
  ],
  "layout": "stack",
  "view": "table",
  "actions": [
    {
      "name": "heat_lookup",
      "label": "反查炉温",
      "path": "/heat_lookups/lookup",
      "fields": [
        {
          "name": "code",
          "label": "倒查单号",
          "kind": "text",
          "initial": "HL-01"
        },
        {
          "name": "profile",
          "label": "曲线版本",
          "kind": "text",
          "initial": "PRO-24"
        },
        {
          "name": "thick",
          "label": "片厚 mm",
          "kind": "float",
          "initial": 4
        },
        {
          "name": "target",
          "label": "工艺目标弯度 mm",
          "kind": "float",
          "initial": 13
        },
        {
          "name": "measured",
          "label": "成品弯度 mm",
          "kind": "float",
          "initial": 11.147
        }
      ],
      "help": "同一倒查单号重复提交只回单、不新增；缺拟合参数的老曲线只供查阅。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已写入"
    },
    {
      "name": "heat_lookup_confirm",
      "label": "确认倒查炉温",
      "path": "/heat_lookups/confirm",
      "fields": [
        {
          "name": "code",
          "label": "倒查单号",
          "kind": "text",
          "initial": "HL-01"
        }
      ],
      "help": "并发确认时以先确认的炉温和曲线版本为准，重复确认被拒绝。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已确认"
    }
  ]
};

        export const {title} = page;
        export const key = "heat_lookups";
        export async function render(root, role) {
          await workspace(root, role, page);

        }

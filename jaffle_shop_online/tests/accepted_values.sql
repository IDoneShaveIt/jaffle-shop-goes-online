{{
    config(
        severity='warn',
        meta={'owner': ['joost@elementary-data.com'], 'description': 'hibob-demo', 'quality_dimension': 'accuracy'},
        tags=['hibob']
    )
}}

select * from {{ ref('orders') }}
where status not in ('placed','shipped','completed','return_pending','returned')

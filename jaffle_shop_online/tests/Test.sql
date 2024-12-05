{{
    config(
        severity='error',
        meta={'owner': ['maayan+172@elementary-data.com'], 'description': 'Test'}
    )
}}

select * from {{ ref('orders') }}
where status not in ('placed','shipped','completed','return_pending','returned')

{{
    config(
        meta={'owner': ['Ella'], 'description': 'checks LTV is not too high', 'quality_dimension': 'accuracy'},
        severity='error'
    )
}}

SELECT customer_email
FROM {{ ref('customers') }}
WHERE customer_lifetime_value > 100000

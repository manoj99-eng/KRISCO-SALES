from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_upc(item):
    return item.get('upc')


@register.filter(name='unique_brands')
def unique_brands(queryset):
    unique_brands = set()
    if queryset:
        for record in queryset:
            if record.description:
                brand = record.description.split('-')[0]
                unique_brands.add(brand)
    return sorted(unique_brands)

@register.filter(name='unique_seller_categories')
def unique_seller_categories(queryset):
    unique_categories = set()
    if queryset:
        for record in queryset:
            unique_categories.add(record.sellercategory)
    return sorted(unique_categories)


@register.filter
def get_brand_field(brand_discount_fields, brand):
    return brand_discount_fields.get(brand, "")
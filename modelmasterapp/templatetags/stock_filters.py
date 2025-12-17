from django import template
import re

register = template.Library()

@register.filter
def highlight_plating_color(plating_stock_no):
    """
    Highlights ONLY the plating color character in plating stock number with PRIMARY COLOR + BOLD
    Example: 1805SBP02 -> 1805<b style="color: #028084; font-weight: bold;">S</b>BP02
    Example: 2617SAD02 -> 2617<b style="color: #028084; font-weight: bold;">S</b>AD02
    """
    if not plating_stock_no:
        return plating_stock_no
    
    try:
        # Handle stock numbers with "/" (e.g., "2648QAA02/BRN")
        base_stock = plating_stock_no.split("/")[0] if "/" in plating_stock_no else plating_stock_no
        
        # Updated Pattern: ModelNumber + ColorCode + Suffix (flexible suffix length)
        # Example: 1805SBP02 -> 1805(S)(BP02), 2617SAD02 -> 2617(S)(AD02)
        pattern = r'^(\d+)([A-Z])([A-Z]+02)$'
        match = re.match(pattern, base_stock)
        
        if match:
            model_no, color_code, suffix = match.groups()
            
            # Add the additional identifier if present
            additional_part = ""
            if "/" in plating_stock_no:
                additional_part = "/" + plating_stock_no.split("/")[1]
            
            # Return with ONLY the color code: PRIMARY COLOR + BOLD + larger font
            highlighted = f'{model_no}<span style="color: #028084; font-weight: bold; font-size: 1.1em;">{color_code}</span>{suffix}{additional_part}'
            return highlighted
        else:
            # If pattern doesn't match, return original without styling
            return plating_stock_no
            
    except Exception as e:
        # On any error, return original without styling
        return plating_stock_no

@register.filter
def highlight_polish_finish(polishing_stock_no):
    """
    Highlights ONLY the polish finish character in polishing stock number with PRIMARY COLOR + BOLD
    Example: 1805XBP02 -> 1805X<b style="color: #028084; font-weight: bold;">B</b>P02
    Example: 2617XAD02 -> 2617X<b style="color: #028084; font-weight: bold;">A</b>D02
    """
    if not polishing_stock_no:
        return polishing_stock_no
    
    try:
        # Handle stock numbers with "/" (e.g., "1805XBP02/EXTRA")
        base_stock = polishing_stock_no.split("/")[0] if "/" in polishing_stock_no else polishing_stock_no
        
        # Updated Pattern: ModelNumber + X + PolishCode + RestOfSuffix
        # Example: 1805XBP02 -> 1805(X)(B)(P02), 2617XAD02 -> 2617(X)(A)(D02)
        pattern = r'^(\d+)(X)([A-Z])([A-Z]+02)$'
        match = re.match(pattern, base_stock)
        
        if match:
            model_no, x_code, polish_code, version_suffix = match.groups()
            
            # Add the additional identifier if present
            additional_part = ""
            if "/" in polishing_stock_no:
                additional_part = "/" + polishing_stock_no.split("/")[1]
            
            # Return with ONLY the polish code: PRIMARY COLOR + BOLD + larger font
            highlighted = f'{model_no}{x_code}<span style="color: #028084; font-weight: bold; font-size: 1.1em;">{polish_code}</span>{version_suffix}{additional_part}'
            return highlighted
        else:
            # If pattern doesn't match, return original without styling
            return polishing_stock_no
            
    except Exception as e:
        # On any error, return original without styling
        return polishing_stock_no

@register.filter
def safe_html(value):
    """
    Mark string as safe HTML to prevent escaping
    """
    from django.utils.safestring import mark_safe
    return mark_safe(value)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

# filepath: your_app/templatetags/custom_tags.py

@register.filter
def split(value, delimiter=','):
    """Splits the string by the given delimiter."""
    return value.split(delimiter)


@register.filter
def strip(value):
    """Removes leading and trailing whitespace."""
    if isinstance(value, str):
        return value.strip()
    return value
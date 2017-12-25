def get_settings(setting_model):
    try:
        settings = setting_model.objects.filter(is_active = 1).order_by('is_active')
        current_setting = settings[0]
        return current_setting
    except setting_model.DoesNotExist:
        raise AdvisorWrongSetting('Cobweb Wrong Setting.')

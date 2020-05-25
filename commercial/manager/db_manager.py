from commercial.models import CommercialActivity, Club, ActivityParticipant, ClubCouponTemplate, ClubUserInfo


def get_commercial_activity_by_id_db(activity_id):
    try:
        return CommercialActivity.objects.get(id=activity_id)
    except CommercialActivity.DoesNotExist:
        return None


def get_commercial_activities_by_ids_db(ids):
    return CommercialActivity.objects.filter(id__in=ids)


def get_commercial_activities_by_club_id_db(club_id, start, end):
    return CommercialActivity.objects.filter(club_id=club_id).order_by('-created_time')[start: end]


def get_club_by_id_db(club_id):
    try:
        return Club.objects.get(id=club_id)
    except Club.DoesNotExist:
        return None


def get_club_by_account_and_password(account, password):
    try:
        return Club.objects.get(account=account, password=password)
    except Club.DoesNotExist:
        return None


def create_club_user_info_by_user_info_and_club(user_info, club):
    return ClubUserInfo.objects.get_or_create(user_info=user_info, club=club)


def get_coupon_template_by_id_db(template_id):
    try:
        return ClubCouponTemplate.objects.get(id=template_id)
    except ClubCouponTemplate.DoesNotExist:
        return None


def get_club_by_ids_db(club_ids):
    return Club.objects.filter(id__in=club_ids)


def create_activity_participate_record_db(activity_id, user_info_id, name, cellphone, num, hint):
    return ActivityParticipant.objects.get_or_create(activity_id=activity_id, user_info_id=user_info_id, defaults={
        'name': name, 'cellphone': cellphone, 'num': num, 'hint': hint
    })

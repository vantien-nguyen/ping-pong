from rest_framework import serializers


class ConfigSerializer(serializers.Serializer):
    m = serializers.IntegerField(min_value=1)
    n = serializers.IntegerField(min_value=1)


class PixelSerializer(serializers.Serializer):
    x = serializers.IntegerField(min_value=0)
    y = serializers.IntegerField(min_value=0)
    color = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=255), min_length=3, max_length=3
    )


class PingPongSerializer(serializers.Serializer):
    m = serializers.IntegerField()
    n = serializers.IntegerField()
    image = serializers.DictField(child=PixelSerializer())
    used_colors = serializers.ListField()
    next_url = serializers.URLField()
    main_url = serializers.URLField()

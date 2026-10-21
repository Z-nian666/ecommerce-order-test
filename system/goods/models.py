from django.db import models

class Goods(models.Model):
    name = models.CharField(max_length=100,verbose_name="商品名称")
    price = models.FloatField(verbose_name="价格")
    stock = models.IntegerField(default=0,verbose_name="库存")
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "goods"
        verbose_name = "商品"
    def __str__(self):
        return self.name
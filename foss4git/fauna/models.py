from django.db import models

class Animale(models.Model):
    """Modello per rappresentare gli animali"""
    nome = models.CharField(max_length=50, unique = True)
    foto = models.ImageField(upload_to='animali.foto',blank=True, null=True)

    def __unicode__(self):
        return '%s' % (self.nome)

    class Meta:
        ordering = ['nome']
        verbose_name_plural = "Animali"

class Avvistamento(models.Model):
    """Modello spaziale per rappresentare gli avvistamenti"""

    data = models.DateTimeField()
    note = models.TextField(blank=True, null=True)
    animale = models.ForeignKey(Animale)

    def __unicode__(self):
        return '%s' % (self.data)

    class Meta:
        ordering = ['data']
        verbose_name_plural = "Avvistamenti"


# -*- coding: utf-8 -*-
# © 2019 Projet Yazılım ve Danışmanlık A.Ş (www.bulutkobi.io)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, tools, api


class VirtualAgingPartnerBalanceReport(models.Model):
    _name = "virtual.aging.partner.balance.report"

    partner_id = fields.Many2one('res.partner', string='Partner', index=True)
    account_id = fields.Many2one('account.account', string='Account', index=True)
    move_id = fields.Many2one('account.move', string='Account Move', index=True)
    due_date = fields.Date(string='Due Date')
    balance = fields.Float(string='Balance')
    user_id = fields.Many2one('res.users', string='Salesman')
    company_id = fields.Many2one('res.company', string='Company')

    @api.model_cr_context
    def _auto_init(self):
        res = super(VirtualAgingPartnerBalanceReport, self)._auto_init()
        self.env.cr.execute("""DROP FUNCTION IF EXISTS virtual_aging_partner_balance_report() CASCADE;""")
        self.env.cr.execute("""truncate virtual_aging_partner_balance_report;""")
        self.env.cr.execute("""
        CREATE OR REPLACE FUNCTION virtual_aging_partner_balance_report()
          RETURNS TABLE(o_partner_id integer, o_account_id character varying, o_move_id integer, o_evrak_tarihi_a date, o_tutar numeric, o_tahsil_edilen numeric, o_bakiye numeric, o_evrak_tarihi_b date, o_tarih date, o_tutar_b numeric, o_bakiye_b numeric, o_bakiye_sign integer, o_company_id integer)
         LANGUAGE plpgsql
         IMMUTABLE COST 1000 ROWS 20000
        AS $function$
        DECLARE
    tahsil_edilen_borc numeric := 0;
    tahsil_edilen_tahsilat numeric := 0;
    current_partner_id integer;
    account_ids integer ARRAY;
    borc RECORD;        
    alacak RECORD;      
    
    borc_table CURSOR FOR (
        SELECT 
                        aml.partner_id
                        ,aml.account_id
                        --,aml.id as moveline_id
                        ,aml.move_id
                        ,aml.date as evrak_tarihi   
                        --,sum(aml.line_balance) as tutar
                        ,sum(aml.balance) as tutar,
                        aml.company_id
        FROM account_move_line aml 
        
        WHERE aml.account_id IN (SELECT id FROM account_account WHERE (code like ('120%')  or code like ('320%') or code like ('329%'))) --or code like ('195%') talep doğrultusunda kaldırıldı.(1.11.2018 - Hızır Bey)
            and aml.partner_id= current_partner_id and aml.balance>0 
        GROUP BY aml.partner_id
                        ,aml.account_id
                        ,aml.move_id
                        ,aml.date,
                        aml.company_id
        ORDER BY aml.date, aml.move_id asc); --evrak tarihinin yanına id için de bir sıralama eklenecek
    alacak_table CURSOR FOR (
        SELECT 
                        aml.partner_id
                        ,aml.account_id
                        --,aml.id as moveline_id
                        ,aml.move_id
                        ,aml.date as evrak_tarihi   
                       -- ,sum(aml.line_balance) as tutar
                       ,sum(aml.balance) as tutar,
                        aml.company_id
        FROM account_move_line aml 
        WHERE  aml.account_id IN (SELECT id FROM account_account WHERE (code like ('120%') or code like ('320%') or code like ('329%'))) 
            and aml.partner_id= current_partner_id and aml.balance<=0 
        GROUP BY aml.partner_id
                        ,aml.account_id
                        ,aml.move_id
                        ,aml.date,
                        aml.company_id       
        ORDER BY aml.date, aml.move_id asc);
        
    partner_table CURSOR FOR (
        SELECT id FROM res_partner order by id asc
    );
BEGIN
    --Partnerlerın borçlarını bul       
    FOR partner IN partner_table LOOP
        current_partner_id:= partner.id;
        
        open alacak_table;
        open borc_table;
        
        tahsil_edilen_borc := 0;
        tahsil_edilen_tahsilat := 0;
        FETCH NEXT FROM alacak_table INTO alacak;
        FETCH NEXT FROM borc_table INTO borc;
        WHILE true LOOP
            --Tahsilat Bittiyse Aşağıda Gitme sadece Borcu Yaz ve Yukarı Sıradaki Borçlara Dön
            IF (alacak IS NULL) THEN
                IF borc IS NULL and alacak IS NULL THEN
                    EXIT;
                END IF;
                --Sadece Borcu Insert Et Sonuç Tablosuna
                o_partner_id :=borc.partner_id;
                o_company_id :=borc.company_id;
                o_account_id :=borc.account_id;
                o_move_id :=borc.move_id;
                o_evrak_tarihi_a := borc.evrak_tarihi;
                o_tutar := borc.tutar;
                o_tahsil_edilen:= 0;
                o_bakiye := borc.tutar;
                o_evrak_tarihi_b := null;
                o_tutar_b := null;
                o_bakiye_b :=null;
                o_bakiye_sign :=1;--borçtan bakiye verdi
                o_tarih :=o_evrak_tarihi_a;                
                IF(o_evrak_tarihi_a is NULL) THEN
                    o_tarih:= o_evrak_tarihi_b;
                END IF;
                
                RETURN NEXT;
                
                FETCH NEXT FROM borc_table INTO borc;
                CONTINUE;
            END IF;
        --------------------------------------------------
            IF (borc IS NULL) THEN
                IF (borc IS NULL and alacak IS NULL) THEN
                    EXIT;
                END IF;
                --Sadece Borcu Insert Et Sonuç Tablosuna
                o_partner_id :=alacak.partner_id;
                o_company_id :=alacak.company_id;
                o_account_id :=alacak.account_id;
                o_move_id :=alacak.move_id;
                o_evrak_tarihi_a := null;
                o_tutar := 0;
                o_tahsil_edilen:= 0;
                o_bakiye := 0;
                o_evrak_tarihi_b := alacak.evrak_tarihi;
                o_tutar_b := alacak.tutar;
                o_bakiye_b :=abs(alacak.tutar) ;
                o_bakiye_sign :=2;--alacaktan bakiye verdi
                
                o_tarih :=o_evrak_tarihi_a;                
                IF(o_evrak_tarihi_a is NULL) THEN
                    o_tarih:= o_evrak_tarihi_b;
                END IF;
                
                RETURN NEXT;
                
                FETCH NEXT FROM alacak_table INTO alacak;
                CONTINUE;
            END IF;
        --------------------------------------------------          
            --BORCU DAĞIT (BORÇ'TAN ÖNCEKİ TAHSİLATI DÜŞ ALACAK İLE KARŞILAŞTIR)
            IF((borc.tutar-tahsil_edilen_borc) > (abs(alacak.tutar)-tahsil_edilen_tahsilat)) THEN 
                --Insert Sonuç Tablosu
                --Sadece Borcu Insert Et Sonuç Tablosuna
                 o_partner_id :=borc.partner_id;
                 o_company_id :=borc.company_id;
                 o_account_id :=borc.account_id;
                 o_move_id :=borc.move_id;
                 o_evrak_tarihi_a := borc.evrak_tarihi;
                 o_tutar := borc.tutar;
                 o_tahsil_edilen := (abs(alacak.tutar)-tahsil_edilen_tahsilat);
                 o_bakiye := (borc.tutar-tahsil_edilen_borc) - o_tahsil_edilen;
                 o_evrak_tarihi_b := alacak.evrak_tarihi;
                 o_tutar_b := alacak.tutar;
                 o_bakiye_b :=0;
                 o_bakiye_sign :=0; --borç bitmedi
                tahsil_edilen_borc:= tahsil_edilen_borc + (abs(alacak.tutar)-tahsil_edilen_tahsilat);
                tahsil_edilen_tahsilat:= 0;
                
                o_tarih :=o_evrak_tarihi_a;                
                IF(o_evrak_tarihi_a is NULL) THEN
                    o_tarih:= o_evrak_tarihi_b;
                END IF;
                
                FETCH NEXT FROM alacak_table INTO alacak;
                
                -- Alacak Bittiyse bu borç bakiye verir.
                IF (alacak IS NULL) THEN
                     o_bakiye_sign :=1;
                     FETCH NEXT FROM borc_table INTO borc;
                END IF;
                
                RETURN NEXT;
                
                CONTINUE;
            END IF;
            IF((borc.tutar-tahsil_edilen_borc) < (abs(alacak.tutar)-tahsil_edilen_tahsilat)) THEN 
                --Insert Sonuç Tablosu
                o_partner_id :=borc.partner_id;
                o_company_id :=borc.company_id;
                o_account_id :=borc.account_id;     
                o_move_id :=borc.move_id;           
                o_evrak_tarihi_a := borc.evrak_tarihi;
                o_tutar := borc.tutar;
                o_tahsil_edilen:= borc.tutar-tahsil_edilen_borc;
                o_bakiye := 0;
                o_evrak_tarihi_b := alacak.evrak_tarihi;
                o_tutar_b := alacak.tutar;
                o_bakiye_b :=(abs(alacak.tutar)-tahsil_edilen_tahsilat) - o_tahsil_edilen ;
                o_bakiye_sign :=0; -- borç bitti
                                
                                                          
                tahsil_edilen_tahsilat:= tahsil_edilen_tahsilat + (borc.tutar-tahsil_edilen_borc) ;
                tahsil_edilen_borc:=0;
                                                  
                o_tarih :=o_evrak_tarihi_a;                
                IF(o_evrak_tarihi_a is NULL) THEN
                    o_tarih:= o_evrak_tarihi_b;
                END IF;
                
                FETCH NEXT FROM borc_table INTO borc;
                
                -- borc Bittiyse bu alacak bakiye verir.
                IF (borc IS NULL) THEN
                     o_bakiye_sign :=2;
                     FETCH NEXT FROM alacak_table INTO alacak;
                END IF;
                RETURN NEXT;    
                
                CONTINUE;
            END IF;
            IF((borc.tutar-tahsil_edilen_borc) = (abs(alacak.tutar)-tahsil_edilen_tahsilat)) THEN 
                --Insert Sonuç Tablosu
                o_partner_id :=borc.partner_id;
                o_company_id :=borc.company_id;
                o_account_id :=borc.account_id;
                o_move_id :=borc.move_id;   
                o_evrak_tarihi_a := borc.evrak_tarihi;
                o_tutar := borc.tutar;
                o_tahsil_edilen:=  borc.tutar-tahsil_edilen_borc;
                o_bakiye := 0;
                o_evrak_tarihi_b := alacak.evrak_tarihi;
                o_tutar_b := alacak.tutar;
                o_bakiye_b :=0;
                --o_bakiye_sign :=false;
                o_bakiye_sign :=0; --tahsil edildi. bakiye yok
                
                o_tarih :=o_evrak_tarihi_a;                
                IF(o_evrak_tarihi_a is NULL) THEN
                    o_tarih:= o_evrak_tarihi_b;
                END IF;
                
                RETURN NEXT;                                              
                tahsil_edilen_tahsilat:= 0;
                tahsil_edilen_borc:=0;      
                FETCH NEXT FROM alacak_table INTO alacak;
                FETCH NEXT FROM borc_table INTO borc;
            END IF;
        END LOOP;
        close borc_table;
        close alacak_table;
    END LOOP;
END;
$function$  

""")
        self.env.cr.execute("""select virtual_aging_partner_balance_report();""")
        fetched_data = self.env.cr.dictfetchall()
        for y in fetched_data:
            yy = y['virtual_aging_partner_balance_report'].replace('(', '').replace(')', '').split(',')
            salesman_id = self.env['res.partner'].search([('id', '=', int(yy[0]))]).user_id.id
            if yy[11] == '1':
                balance = float(yy[6])
            elif yy[11] == '2':
                balance = float(yy[10]) * -1
            else:
                balance = 0
            values = {'partner_id': int(yy[0]), 'account_id': int(yy[1]), 'move_id': int(yy[2]), 'due_date': yy[8],
                        'balance': balance, 'user_id': salesman_id, 'company_id': int(yy[12])}
            self.create(values)
        return res
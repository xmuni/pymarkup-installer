html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Old catalog</title>
    <link rel="stylesheet" href="main.css">

    <style>
        @page {

            size: a4 portrait;
            @frame content_frame {          /* Content Frame */
                left: 40pt; width: 512pt; top: 40pt; height: 750pt;
            }
            @frame footer_frame {
                -pdf-frame-content: footer_content;
                left: 50pt; width: 512pt; top: 800pt; height: 20pt;
            }
        }
    </style>

    {% if css %}
    <style type="text/css">
        {{ css }}
    </style>
    {% else %}
        <h1>ERROR LOADING CSS</h1>
        <hr/>
    {% endif %}

    {% if preview %}
        <style type="text/css">
            table img {
                width: 80px;
            }
        </style>
    {% endif %}

</head>

<body>

    {% if not preview %}
    <div id="footer_content">
        {{ localized.fullname }}: 
        _____________________________
        {{ localized.signed }}: 
        _____________________________
        {{ localized.page }} <pdf:pagenumber>
        {{ localized.of }} <pdf:pagecount>
    </div>
    {% endif %}

    <main>

    <header>
        <table>

            <tr>
                <td class="left">
                    <b> INDUSTRIA LATERIZI
                    <br>VITTORIO CARRARO & C. S.A.S.</b>
                    <br>Via Borgo Botteghe, 102
                    <br>35028 Piove di Sacco (PD)
                    <br>Italia
                    <br>Tel & Fax: +39 049 9775015
                    <br>P. IVA: 00313130288
                    <br>Codice destinatario: W7YVJK9
                </td>
                <td class="right">
                    {{ cliente | add_br_tags }}
                </td>
            </tr>

        </table>
    </header>

    <p><b>
        {% if lingua == 'it' %}
            Data:
        {% else %}
            Date:
        {% endif %}
    </b> {{ data }}</p>

    <p>
        {% if render_estimate %}
            {{ preventivo or localized.estimate }}
        {% elif render_proforma %}
            {{ proforma or localized.proforma }}
        {% endif %}
    </p>

    {% for table in tables %}
    <table id=items-sold>

        <tr>
            <th class="qty">{{ localized.qty }}<br/><small>Mq</small></th>
            <th class="wgt">{{ localized.wgt }}<br/><small>Kg</small></th>
            <th class="pcs">{{ localized.pcs }}<br/></th>
            {% if table.img %}
            <th class="img"><br/></th>
            {% endif %}
            <th class="description">{{ localized.desc }}<br/></th>
            <th class="price unit" colspan="2">{{ localized.price_unit }}<br/></th>
            <th class="subtot">{{ localized.subtot }}<br/></th>
        </tr>
        
        {% for row in table.riga %}
        
        <tr class="{% if row.even %} even {% endif %} {% if row.error %}error{% endif %}">
            <td class="qty" rowspan="{% if 'sub' in row %}{{ 1 + row.sub|length }}{% else %}1{% endif %}">
                {% if row.mq %}
                    {{ row.mq | format_number }}
                {% else %}
                    {{ tag_br }}
                {% endif %}
            </td>

            <td class="wgt">
                {% if row.kg and 'sub' not in row %}
                    {{ row.kg | round | int }}
                {% else %}
                    {{ tag_br }}
                {% endif %}
            </td>
            
            <td class="pcs">
                {{ row.pz|round|int if row.pz else tag_br }}
            </td>
            
            {% if table.img %}
            <td class="img" rowspan="{% if 'sub' in row %}{{ 1 + row.sub|length }}{% else %}1{% endif %}">
                {% if row.imgpath %}
                    <img src="{{ row.imgpath }}" alt="">
                {% else %}
                    <br/>
                {% endif %}
            </td>
            {% endif %}

            <td class="description">
                {{ row.error }}
                {{ row.desc | add_br_tags if row.desc else tag_br }}
                {% if row.nota %}
                    {{ tag_br }}{{ row.nota | add_br_tags }}
                {% endif %}
                {% if preview %}
                    {{ row.info | format_info if row.info else pass }}
                {% endif %}
            </td>
            
            <td class="price" rowspan="{% if 'sub' in row %}{{ 1 + row.sub|length }}{% else %}1{% endif %}">
                € {{ row.eur | format_number }}
            </td>

            <td class="unit" rowspan="{% if 'sub' in row %}{{ 1 + row.sub|length }}{% else %}1{% endif %}">/ {{ row.um }}</td>

            <td class="subtot" rowspan="{% if 'sub' in row %}{{ 1 + row.sub|length }}{% else %}1{% endif %}">
                € {{ row.tot | format_number }}
            </td>

        </tr>

            {% for subrow in row.sub %}
            <tr class="{% if row.even %} even {% endif %} {% if row.error %}error{% endif %}">
                <td class="wgt">{{ subrow.kg|round|int if subrow.kg else tag_br }}</td>
                <td class="pcs">{{ subrow.pz|round|int if subrow.pz else tag_br }}</td>
                <td class="description">
                    {{ row.error }}
                    {{ subrow.desc | add_br_tags if subrow.desc else tag_br }}
                </td>
            </tr>
            {% endfor %}

        {% endfor %}
        
        <!-- Total (no vat) -->
        <tr class="row-subtotal">
            <td colspan="{% if table.img %}5{% else %}4{% endif %}"></td>
            <td colspan="2">{{ localized.subtot }}</td>
            <td>€ {{ table.tot | format_number }}</td>
        </tr>

        <!-- Vat only -->
        <tr class="row-vat">
            <td colspan="{% if table.img %}5{% else %}4{% endif %}">
                {{ table.nota }}
            </td>
            <td colspan="2">{{ localized.vat }} {{ table.iva }}%</td>
            <td>€ {{ (table.tot * table.iva / 100) | format_number }}</td>
        </tr>

        <!-- Total (with vat) -->
        <tr class="row-total">
            <td colspan="{% if table.img %}5{% else %}4{% endif %}" class="align-left">
                {{ table.kg | round | int }} kg tot.
            </td>
            <td colspan="2">{{ localized.tot }}</td>
            <td>€ {{ (table.tot + table.tot * table.iva / 100) | format_number }}</td>
        </tr>

    </table>
    {% endfor %}

    <section id="notes">
        {% if render_estimate %}

        {{ notes_html }}

        {% if preview %}
            <br/>
            <br/>
            <br/>
        {% endif %}
        
        {% elif render_proforma %}
            
            <br/>
            <br/>
            <p>Dati per effettuare il pagamento:</p>
            <p>IBAN 123ABC345DEF678GHI90</p>

        {% endif %}
    </section>

    </main>
    
</body>
</html>
'''

css = '''

/* Normal */
@font-face {
    font-family: Arial;
    src: url("D:/Desktop/Dev/PyMarkup/toml_testing/arial-unicode-ms.ttf");
}

/* Bold */
@font-face {
    font-family: Arial;
    src: url("D:/Desktop/Dev/PyMarkup/toml_testing/arialb.ttf");
    font-weight: bold;
 }

/* Italic */
@font-face {
    font-family: Arial;
    src: url("D:/Desktop/Dev/PyMarkup/toml_testing/ariali.ttf");
    font-style: italic;
}

/* Bold and italic */
@font-face {
    font-family: Arial;
    src: url("D:/Desktop/Dev/PyMarkup/toml_testing/arialbi.ttf");
    font-weight: bold;
    font-style: italic;
}

body {
    font-size: 12px;
    font-family: Arial, Helvetica, sans-serif;
}

table {
    -pdf-keep-in-frame-mode: shrink;
}

p {
    /* letter-spacing: 18px; */
    line-height: 18px;
    font-stretch: expanded;
}

header table {
    line-height: 15px;
    margin-bottom: 40px;
    vertical-align: top;
}

header table td {
    vertical-align: top;
}

header table td.right {
    text-align: right;
}

small {
    font-size: 10px;
}


#items-sold {
    margin-top: 15px;
    /* border: 0.2mm solid black; */
}

#items-sold tr {
    border: .2mm solid #ddd;
    border-top: none;
    padding-top: 1mm;
    padding-right: 1mm;
    padding-left: 1mm;
}

#items-sold th {
    background-color: rgb(135, 187, 236);
    /* background-color: rgb(244,244,244); */
    font-weight: bold;
    font-size: 12px;
    padding-top: 1mm;
    padding-right: 1mm;
    padding-left: 1mm;
    vertical-align: top;
    /* text-align: right; */
    border-bottom: none;
}

#items-sold tr td {
    vertical-align: middle;
    text-align: right;
}

#items-sold tr th.qty,
#items-sold tr th.wgt,
#items-sold tr th.pcs,
#items-sold tr td.qty,
#items-sold tr td.wgt,
#items-sold tr td.pcs {
    width: 12mm;
}
#items-sold tr th.price,
#items-sold tr td.price {
    width: 15mm;
}
#items-sold tr th.unit,
#items-sold tr td.unit {
    width: 11mm;
}

#items-sold tr th.img {
    width: 30mm;
}

#items-sold tr td.img {
    padding: 0;
    margin: 0;
}

#items-sold tr td.img img {
    object-fit: cover;
}

#items-sold tr td.description {
    /* width: 55mm; */
    text-align: left;
}

#items-sold tr td.unit {
    text-align: left;
}

#items-sold tr th.subtot,
#items-sold tr td.subtot {
    width: 23mm;
}

#items-sold tr.row-subtotal {
    border-top: .2mm solid black;
    background-color: rgb(244,244,244);
}

#items-sold tr.row-vat {
    background-color: rgb(244,244,244);
}

#items-sold tr.row-total {
    background-color: rgb(244,244,244);
    font-weight: bold;
}

#items-sold tr td.align-left {
    text-align: left;
}

footer p {
    text-align: center;
}

span.info {
    /* color: rgb(196, 82, 82); */
    /* font-weight: bold; */
    /* text-decoration: underline; */
    background-color: rgb(204, 226, 190);
}


/* DDT CSS */

.ddt {
    color: #111;
    line-height: 18px;
}


.ddt td, .ddt th {
    border: .2mm solid #ccc;
    background-color: white;
    /* margin: 1mm; */
    padding-top: 1.2mm;
    padding-left: .5mm;
    vertical-align: center;
    /* font-size: 10px; */
}

td.no-border-right {
    border-right: none;
}

td.no-border-left {
    border-left: none;
}

.no-borders td, .no-borders th, .no-borders tr {
    border: none;
}

.height-low {
    height: 20px;
}

.borders-sides {
    border-left: .2mm solid #ccc;
    border-right: .2mm solid #ccc;
}

.ddt h1, h2, h3, h4, h5, h6 {
    margin: 0;
}

.ddt h6 {
    font-size: 8px;
    font-weight: normal;
}

.ddt h5 {
    font-size: 10px;
    font-weight: normal;
}

.ddt h1 {
    font-size: 22px;
    padding-bottom: 4px;
    color: #333;
}

.ddt td.company {
    width: 300px;
    line-height: 16px;
    text-align: center;
    font-size: 10px;
}

.ddt td.bottom {
    text-align: end;
}

.ddt th {
    font-weight: bold;
}

.narrow {
    width: 80px;
}

.width-med {
    width: 120px;
}

table tr td.min-padding {
    /* padding-top: .1mm; */
    /* margin-top: .1mm; */
    margin: 0;
    height: 19px;
    font-size: 18px;
}

.text-center {
    text-align: center;
}

.text-top {
    text-align: start;
}

.line {
    border-bottom: 1px solid black;
    margin-bottom: 5px;
    background-color: gray;
}

.checkbox {
    font-size: 20px;
}


.low-margin, .low-margin tr {
    margin: 0;
    padding: 0;
    line-height: 0;
}

.space-below {
    padding-bottom: 3px;
}

.row-subtotal,
.row-vat,
.row-total {
    /* font-size: 10px; */
    vertical-align: middle;
}

table tr.even {
    background-color: #f6f6f6;
}

table tr.error,
table tr.even.error {
    background-color: rgb(255, 235, 235);
}

#notes p {
    text-align: justify;
    margin-top: 5px;
}

#notes h1 {
    margin-bottom: 0;
    font-size: 14px;
}


/*
.checkbox {
    height: 40px;
    width: 40px;
    border: 1px solid black;
    background-color: gray;
}

.check {
    height: 30px;
    width: 30px;
    background-color: black;
    color: white;
    margin: auto;
}

img.checkbox {
    height: 10px;
    width: 10px;
    display: inline-block;
}
*/


/*
#ddt-grid {
    display: grid;
    background: black;
    gap: 1px;
    padding: 1px;
    grid-template-columns: repeat(4, 1fr);
}

#ddt-grid div {
    background: white;
    padding: 5px 10px;
}
 */

'''
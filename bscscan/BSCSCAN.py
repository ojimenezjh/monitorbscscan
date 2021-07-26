    #!/usr/bin/env python
#_*_ coding: utf8 _*_

import requests
import json
import time
import sys
from bs4 import BeautifulSoup
# from selenium import webdriver
# from pyvirtualdisplay import Display
# import cfscrape

# proxyraw = "prov2.ignify.xyz:31112:pl2sspnrj:3oZE3eenG2qCNnWn_country-Spain_session-IOQECNZK"
# proxy = str(proxyraw).split(':')

# proxies = {
#   'http': f'http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}',
#   'https': f'https://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}',
#   'no_proxy': 'localhost,127.0.0.1'
# }

Webhook = "https://discord.com/api/webhooks/866828166465847327/FnBcVvMIr7eOuNw8wWt-uQnmm9BScyPWc38zONmLrMZdYeZFTG_tnLtKn_m1klMzfLdN"
wallet = "0x0f526aaa64756e0a4943e25911b85bf2babf18a2"

existentSignal = []

buysDictionary = {}
buysDictionary["tokenName"] = []
buysDictionary["buyPrice"] = []
buysDictionary["tokenQuantity"] = []
buysDictionary["totalTokenQuantity"] = []

contador = 0

while True:

  print(buysDictionary)

  contador = contador+1

  t = time.localtime()
  current_time = time.strftime("%H:%M:%S", t)

  print('Testing '+current_time)

  try:

      source = requests.get('https://bscscan.com/tokentxns?a='+wallet).text
      soup = BeautifulSoup(source, 'lxml')

      tx = soup.find('div',class_='table-responsive')

      if contador == 1:
        txId = "0xc49634bd72b796cc4ba391ffe3ae2690b5ea7319f540f22617d1ca6d73097f76"
      elif contador == 2:
        txId = tx.find('a', class_='myFnExpandBox_searchVal').text
      #tx.find('a', class_='myFnExpandBox_searchVal').text

      if txId in existentSignal:
        print('Repeated')

      else:
        existentSignal.append(txId)

        source2 = requests.get('https://bscscan.com/tx/'+txId).text
        soup2 = BeautifulSoup(source2, 'lxml')

        source3 = requests.get('https://bscscan.com/tx/'+txId+'#internal').text
        soup3= BeautifulSoup(source3, 'lxml')

        if contador == 1:
          inOut = "IN"
        elif contador == 2:
          inOut = "OUT"
        #soup.find('td', class_="text-align").text
        text = 'Tokens Transferred: '
        token = soup2.find_all(lambda tag: tag.name == "span" and text in tag.text)
        bnb = soup2.find('span', class_='text-dark').text

        bnbValue = bnb.replace('BNB: $','')

        if token == []:

            walletFrom = soup2.find('a', id="addressCopy").text

            if walletFrom == wallet:
                walletTo = soup2.find('a', id="contractCopy").text
                print('Transferencia hacia wallet: '+walletTo+' |'+value+' | '+bnb)
            else:
                print('Transferencia desde wallet: '+walletFrom+' |'+value+' | '+bnb)

        else:
            tokenTX = soup2.find_all('span', class_="hash-tag text-truncate mr-1")

            if 'IN' in inOut:
              contractUrl = tokenTX[1].find_all('a', href=True)

            elif 'OUT' in inOut:
              contractUrl = tokenTX[0].find_all('a', href=True)

            for a in contractUrl:
                contractUrl = (a.get('href'))
                contractUrl = contractUrl[(-len(contractUrl)+7):(-len(contractUrl)+7)+42]

            tokenSource= requests.get('https://bscscan.com/token/'+contractUrl).text
            tokenSoup = BeautifulSoup(tokenSource, 'lxml')
            tokenName = tokenSoup.find('span', class_="text-secondary small").text

            try:
                cg = 'https://www.coingecko.com/es/monedas/'+contractUrl
            except:
                cg = 'No'

            try:
                cmc = 'https://coinmarketcap.com/currencies/'+(tokenName.strip().replace(' ', '-').lower())
            except:
                cmc = 'No'

            tokenQuantity = (soup.find_all('td')[7].text).strip().replace(',','')
            bnbTotal = (soup3.find_all('tr'))
            print(tokenQuantity)

            bnbTotalQuantity = []
            pricePosition = 4

            for bnb in bnbTotal:
              try:
                bnb = (soup3.find_all('td')[pricePosition].text).strip().replace(' BNB','').replace(',','')
                if float(bnb) not in bnbTotalQuantity:
                  bnbTotalQuantity.append(float(bnb))
                else:
                  pass
              except:
                pass
              pricePosition = pricePosition+6

            bnbTotalQuantity = str(sum(bnbTotalQuantity))
            txValue = float(bnbTotalQuantity) * float(bnbValue)
            precioCompraVenta = str(txValue / float(tokenQuantity))
            holders = tokenSoup.find('div', class_="mr-3").text
            poocoin = 'https://poocoin.app/tokens/'+contractUrl

            #print('From: '+contractUrl, precioCompra,tokenNameFrom, bnbTXPrice, bnbTX, tokenPriceFrom, quantityTo, holdersFrom, 'To: '+contractUrlTo, tokenNameTo, holdersTo, value)

            if 'IN' in inOut:
                if tokenName not in buysDictionary["tokenName"]:
                  buysDictionary["tokenName"].append(tokenName)
                  buysDictionary["buyPrice"].append(precioCompraVenta)
                  buysDictionary["tokenQuantity"].append(tokenQuantity)
                  buysDictionary["totalTokenQuantity"].append(tokenQuantity)

                else:
                  idx = buysDictionary["tokenName"].index(tokenName)
                  buysDictionary["tokenQuantity"][idx] = float(buysDictionary["tokenQuantity"][idx]) + float(tokenQuantity)
                  buysDictionary["buyPrice"][idx] = mean([float(buysDictionary["buyPrice"][idx])], [float(precioCompraVenta)])

                def sendwebhook():
                  data={
                          "content": "Nueva señal de compra: "+tokenName,
                          "embeds": [
                  {
                    "title": "Compra en Bogged",
                    "url": "https://bogged.finance/swap?tokenIn=BNB&tokenOut="+contractUrl,
                    "color": 48895,
                    "fields": [
                      {
                        "name": "Token recibido",
                        "value": tokenName
                      },
                      {
                        "name": "Precio de compra",
                        "value": '$'+precioCompraVenta
                      },
                      {
                        "name": "Valor Transacción (BNB, USD)",
                        "value": bnbTotalQuantity+' BNB / $'+str(txValue)
                      },
                      {
                        "name": "Holders",
                        "value": holders
                      },
                      {
                        "name": "Contrato",
                        "value": contractUrl
                      },
                      {
                        "name": "Gráfico",
                        "value": poocoin
                      },
                      {
                        "name": "ID Transacción",
                        "value": txId
                      },
                      {
                        "name": "CoinGecko",
                        "value": cg
                      },
                      {
                        "name": "CoinMarketCap",
                        "value": cmc
                      }
                    ],
                    "author": {
                      "name": "Pre-listing Bot BSC"
                    },
                    "footer": {
                      "text": "By Darkraken " +current_time
                    },
                  }
                ]
              }
                  try:
                      response = requests.post(Webhook, data=json.dumps(data), headers={'Content-Type': 'application/json'})
                  except:
                      print("Error al enviar el Webhook")

                sendwebhook()
                print('Sended IN')


            elif 'OUT' in inOut:
                if tokenName in buysDictionary["tokenName"]:
                  idx = buysDictionary["tokenName"].index(tokenName)
                  buysDictionary["tokenQuantity"][idx] = float(buysDictionary["tokenQuantity"][idx]) - float(tokenQuantity)

                  operationPercentage = str((100 * float(precioCompraVenta) / float(buysDictionary["buyPrice"][idx])- 100))+' %'
                  quantityPercentage = str((100 * float(tokenQuantity) / float(buysDictionary["totalTokenQuantity"][idx])- 100))+' %'

                  if round(float(buysDictionary["tokenQuantity"][idx]),2) == 0:
                    operationPercentage = operationPercentage+' Todo vendido'
                    quantityPercentage = quantityPercentage+' Todo vendido'
                    del buysDictionary["tokenQuantity"][idx]
                    del buysDictionary["buyPrice"][idx]
                    del buysDictionary["tokenName"][idx]
                    del buysDictionary["totalTokenQuantity"][idx]

                  else:
                    pass               

                  def sendwebhook():
                    data={
                            "content": "Nueva señal de venta: "+tokenName,
                            "embeds": [
                    {
                      "title": "Vende en Bogged",
                      "url": "https://bogged.finance/swap?tokenIn="+contractUrl+"&tokenOut=BNB",
                      "color": 48895,
                      "fields": [
                        {
                          "name": "Token vendido",
                          "value": tokenName
                        },
                        {
                          "name": "Precio medio de compra",
                          "value": buysDictionary["buyPrice"][idx]
                        },
                        {
                          "name": "Precio de venta",
                          "value": '$'+precioCompraVenta
                        },
                        {
                          "name": "Cantidad vendida y % vendido",
                          "value": tokenQuantity+' / '+quantityPercentage
                        },
                                                {
                          "name": "% Profit Operación",
                          "value": operationPercentage
                        },
                        {
                          "name": "Valor recibido (BNB, USD)",
                          "value": bnbTotalQuantity+' BNB / $'+str(txValue)
                        },
                        {
                          "name": "Holders",
                          "value": holders
                        },
                        {
                          "name": "Contrato",
                          "value": contractUrl
                        },
                        {
                          "name": "Gráfico",
                          "value": poocoin
                        },
                        {
                          "name": "ID Transacción",
                          "value": txId
                        },
                        {
                          "name": "CoinGecko",
                          "value": cg
                        },
                        {
                          "name": "CoinMarketCap",
                          "value": cmc
                        }
                      ],
                      "author": {
                        "name": "Pre-listing Bot BSC"
                      },
                      "footer": {
                        "text": "By Darkraken " +current_time
                      },
                    }
                  ]
                }
                    try:
                        response = requests.post(Webhook, data=json.dumps(data), headers={'Content-Type': 'application/json'})
                    except:
                        print("Error al enviar el Webhook")

                  sendwebhook()
                  print('Sended OUT')


                else:
                  pass

            print("Sended")

  except:
    e = sys.exc_info()[1]
    print(e.args[0])

  time.sleep(10)

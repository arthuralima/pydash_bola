#Projeto de Programação Transmissão de Dados
#2020/2
#
#Grupo 9
#Arthur de Araujo C de Lima       15/0005997
#Fernando Barbosa Cardoso         14/0109137
#Gustavo de Medeiros Roarelli     14/0142592

from r2a.ir2a import IR2A
from player.parser import *
import time
import numpy as np

class R2ABola(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.qi = []
        self.throughput = 0
        self.request_time = 0
        self.v_m = 0

    def handle_xml_request(self, msg):
        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):
        parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = parsed_mpd.get_qi()
        
        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        # Tempo que a mensagem será encaminhada para o ConnectionHandler, usado no throughput
        self.request_time = time.perf_counter()
        
        # Parâmetro de controle para adaptar o bitrate ao tamanho do buffer/ 
        V = (self.whiteboard.get_max_buffer_size() - 1) / (self.v_m + 5)
        
        # Lista do tamanho dos buffers
        buffers = self.whiteboard.get_playback_buffer_size()
        
        # Lista com o índice de qualidades
        playback_qi = self.whiteboard.get_playback_qi()
        
        # Buffer zero antes de reproduzir
        if not buffers:
            buffers = ([0, 0], [0, 0])
            
        # Buffer mais recente
        current_buffer = buffers[-1]
        
        m = 0
        
        # Indicice de qualidade(bitrate) maximo dos disponiveis encontrado pela otimizacao de Lyapounov
        for i in range(20):
            uti = np.log(self.qi[i] / self.qi[0])
            m_prob = (V * uti + V * 5 - current_buffer[1]) / self.qi[i]
            if m_prob > m:
                m = m_prob
                selected_qi = i
        
        if playback_qi:
            #Se o bitrate escolhido for maior que o anterior, procura um novo que seja menor ou igual ao throughput do segmento anterior ou do primeiro bitrate (o que for maior)            
            if selected_qi > playback_qi[-1][1]:
                maxim = self.qi[0]
                ml  = 0
                if self.throughput >= self.qi[0]:
                    maxim = self.throughput
                for j in range(20):
                    if self.qi[j] <= maxim and ml  <= j:
                        ml  = j
                
                # Se o novo bitrate estiver entre os antigos índices, ganha um novo valor, se nao recebe o mesmo valor deles
                if ml  >= m:
                    ml  = selected_qi
                elif ml  < playback_qi[-1][1]:
                    ml  = playback_qi[-1][1]
                #nao sacrifica a utilidade
                else:
                    ml  = ml  + 1
                
                selected_qi = ml 
        
        msg.add_quality_id(self.qi[selected_qi])
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        # Tempo do encaminhamento da mensagem para o ConnectionHandler e volta
        t = time.perf_counter() - self.request_time
        
        # Throughput da requisição do segmento de vídeo
        self.throughput = msg.get_bit_length() / t
        
        # Utilização da rede calculada por funcao logaritmica
        self.v_m = np.log(msg.get_quality_id() / self.qi[0])
        
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass
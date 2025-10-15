// React Native Example with Sync Integration
// 需安裝：npm install axios
// 若要 WebSocket：內建 WebSocket API

import React, { useEffect, useState, useCallback } from 'react';
import { SafeAreaView, Text, FlatList, TouchableOpacity, Modal, View, StyleSheet, ActivityIndicator } from 'react-native';
import axios from 'axios';

const BASE_URL = 'http://localhost:8010';

export default function App() {
  const [status, setStatus] = useState('初始化...');
  const [files, setFiles] = useState([]);
  const [etag, setEtag] = useState(null);
  const [selected, setSelected] = useState(null);
  const [content, setContent] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);

  const loadManifest = useCallback(async (force = false) => {
    try {
      setStatus('同步 manifest 中...');
      const headers = {};
      if (!force && etag) headers['If-None-Match'] = etag;
      const resp = await axios.get(`${BASE_URL}/sync/manifest`, { headers, validateStatus: () => true });
      if (resp.status === 304) {
        setStatus('無變更');
        return;
      }
      if (resp.status !== 200) {
        setStatus('Manifest 錯誤: ' + resp.status);
        return;
      }
      setEtag(resp.data.etag);
      setFiles(resp.data.files);
      setStatus(`同步完成 files=${resp.data.file_count}`);
      // 下載差異檔案
      // （示例：僅在點擊時下載內容，也可以預先全下載）
    } catch (e) {
      setStatus('同步失敗: ' + e.message);
    }
  }, [etag]);

  const loadFileContent = async (path) => {
    try {
      setStatus(`下載 ${path} ...`);
      const resp = await axios.get(`${BASE_URL}/sync/file`, { params: { path } });
      setContent(resp.data.content);
      setSelected(path);
      setStatus('完成');
    } catch (e) {
      setStatus('下載失敗: ' + e.message);
    }
  };

  const setupWebSocket = useCallback(() => {
    try {
      const wsUrl = BASE_URL.replace('http', 'ws') + '/ws/sync';
      const ws = new WebSocket(wsUrl);
      ws.onopen = () => { setWsConnected(true); };
      ws.onmessage = (ev) => {
        try {
          const data = JSON.parse(ev.data);
          if (data.type === 'update') {
            loadManifest(true);
          }
        } catch {}
      };
      ws.onclose = () => { setWsConnected(false); setTimeout(setupWebSocket, 5000); };
      ws.onerror = () => { ws.close(); };
    } catch (e) {
      // ignore
    }
  }, [loadManifest]);

  useEffect(() => {
    loadManifest();
    setupWebSocket();
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>Modern Reader React Native Sync</Text>
      <Text style={styles.status}>{status} {wsConnected ? '🟢' : '🔴'}</Text>
      <TouchableOpacity style={styles.refreshBtn} onPress={() => loadManifest(true)}>
        <Text style={styles.refreshText}>手動同步</Text>
      </TouchableOpacity>
      <FlatList
        data={files}
        keyExtractor={(item) => item.path}
        renderItem={({ item }) => (
          <TouchableOpacity style={styles.item} onPress={() => loadFileContent(item.path)}>
            <Text style={styles.itemPath}>{item.path}</Text>
            <Text style={styles.itemMeta}>{item.sha256.slice(0,8)} | {item.category}</Text>
          </TouchableOpacity>
        )}
      />
      <Modal visible={!!selected} animationType="slide" onRequestClose={() => setSelected(null)}>
        <SafeAreaView style={styles.modalContainer}>
          <Text style={styles.modalTitle}>{selected}</Text>
          <View style={styles.modalContentWrapper}>
            <Text style={styles.modalContent}>{content}</Text>
          </View>
          <TouchableOpacity style={styles.closeBtn} onPress={() => setSelected(null)}>
            <Text style={styles.closeText}>關閉</Text>
          </TouchableOpacity>
        </SafeAreaView>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#111', padding: 16 },
  title: { color: '#fff', fontSize: 20, fontWeight: 'bold', marginBottom: 8 },
  status: { color: '#ccc', marginBottom: 12 },
  refreshBtn: { backgroundColor: '#2563EB', padding: 10, borderRadius: 6, marginBottom: 12, alignItems: 'center' },
  refreshText: { color: '#fff', fontSize: 14 },
  item: { paddingVertical: 10, borderBottomColor: '#333', borderBottomWidth: 1 },
  itemPath: { color: '#fff', fontSize: 14 },
  itemMeta: { color: '#888', fontSize: 12 },
  modalContainer: { flex: 1, backgroundColor: '#000', padding: 16 },
  modalTitle: { color: '#fff', fontSize: 18, fontWeight: 'bold', marginBottom: 12 },
  modalContentWrapper: { flex: 1, borderColor: '#222', borderWidth: 1, padding: 8 },
  modalContent: { color: '#ddd', fontSize: 12 },
  closeBtn: { backgroundColor: '#444', padding: 12, borderRadius: 8, alignItems: 'center', marginTop: 12 },
  closeText: { color: '#fff' }
});

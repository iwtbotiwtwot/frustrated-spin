#include <gmpxx.h>
#include <openssl/sha.h>
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <vector>
#include <string>
#include <stdexcept>
#include <unistd.h>

static std::string hex(const unsigned char* data){
 const char* digits="0123456789abcdef";std::string s;
 for(int i=0;i<32;i++){s+=digits[data[i]>>4];s+=digits[data[i]&15];}return s;
}
// Input is exact little-endian coefficient limbs from the GPU, in polynomial order.
// This host stage writes and validates; it does not calculate polynomial products.
extern "C" int write_counts(const char* path,const char* receipt,const uint64_t* data,
 uint64_t length,int limbs,int n,int bound,int step,int kmajor,int state,int fill,int ports){
 FILE* f=nullptr;
 try{
  const int width=(n+8)/8;std::vector<SHA256_CTX> buckets(n+1);
  std::vector<mpz_class> marginals(n+1);mpz_class moments[3],count;
  for(auto& h:buckets)SHA256_Init(&h);
  SHA256_CTX filehash;SHA256_Init(&filehash);
  f=fopen(path,"wb");if(!f)throw std::runtime_error("open");
  std::vector<char> buffer(4*1024*1024);setvbuf(f,buffer.data(),_IOFBF,buffer.size());
  uint64_t records=0;std::vector<unsigned char> record(8+width);
  for(uint64_t index=0;index<length;index++){
   const uint64_t* words=data+index*limbs;bool nonzero=false;
   for(int j=0;j<limbs;j++)nonzero|=words[j]!=0;
   if(!nonzero)continue;
   uint64_t k=kmajor?index/(bound/step+1):index%(n+1);
   uint64_t t=(kmajor?index%(bound/step+1):index/(n+1))*step;
   if(k>(uint64_t)n || t>(uint64_t)bound)throw std::runtime_error("coefficient index");
   mpz_import(count.get_mpz_t(),limbs,-1,8,0,0,words);
   if(mpz_sizeinbase(count.get_mpz_t(),2)>(size_t)width*8)throw std::runtime_error("count width");
   int64_t ec=2*(int64_t)t-bound;int32_t m=2*(int)k-n;
   int64_t energy=ec-fill*((int64_t(m)*m-n)/2);
   if(energy<INT32_MIN || energy>INT32_MAX)throw std::runtime_error("energy width");
   int32_t e=energy;memcpy(record.data(),&e,4);memcpy(record.data()+4,&m,4);
   memset(record.data()+8,0,width);memcpy(record.data()+8,words,std::min(width,limbs*8));
   if(fwrite(record.data(),record.size(),1,f)!=1)throw std::runtime_error("write");
   SHA256_Update(&filehash,record.data(),record.size());
   SHA256_Update(&buckets[k],&ec,8);SHA256_Update(&buckets[k],record.data()+8,width);
   marginals[k]+=count;moments[0]+=count;moments[1]+=count*energy;
   moments[2]+=(count*energy)*energy;records++;
  }
  if(fflush(f)||fsync(fileno(f)))throw std::runtime_error("flush");
  fclose(f);f=nullptr;
  for(int k=0;k<=n;k++){
   int q=k-__builtin_popcount((unsigned)state);mpz_class expected=0;
   if(q>=0 && q<=n-ports)mpz_bin_uiui(expected.get_mpz_t(),n-ports,q);
   if(expected!=marginals[k])throw std::runtime_error("magnetization marginal");
  }
  SHA256_CTX canon;SHA256_Init(&canon);uint32_t prefix[2]={(uint32_t)n,(uint32_t)state};SHA256_Update(&canon,prefix,8);
  unsigned char digest[32];for(auto& h:buckets){SHA256_Final(digest,&h);SHA256_Update(&canon,digest,32);}
  SHA256_Final(digest,&canon);auto canonical=hex(digest);SHA256_Final(digest,&filehash);auto hash=hex(digest);
  // Full durable file readback, independent of the write buffer.
  SHA256_CTX check;SHA256_Init(&check);f=fopen(path,"rb");if(!f)throw std::runtime_error("readback open");
  size_t got;while((got=fread(buffer.data(),1,buffer.size(),f)))SHA256_Update(&check,buffer.data(),got);
  if(ferror(f))throw std::runtime_error("readback");fclose(f);f=nullptr;SHA256_Final(digest,&check);
  if(hex(digest)!=hash)throw std::runtime_error("readback hash");
  f=fopen(receipt,"w");if(!f)throw std::runtime_error("receipt");
  fprintf(f,"{\"joint_row_sha256\":\"%s\",\"binary_data_sha256\":\"%s\",\"records\":%llu,\"bytes\":%llu,\"moments\":[\"%s\",\"%s\",\"%s\"]}\n",canonical.c_str(),hash.c_str(),(unsigned long long)records,(unsigned long long)(records*(8+width)),moments[0].get_str().c_str(),moments[1].get_str().c_str(),moments[2].get_str().c_str());
  if(fflush(f)||fsync(fileno(f)))throw std::runtime_error("receipt flush");fclose(f);return 0;
 }catch(const std::exception& e){if(f)fclose(f);fprintf(stderr,"write_counts: %s\n",e.what());return 1;}
}
